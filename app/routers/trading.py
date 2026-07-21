from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import json

from app.database import get_db
from app.schemas.trading import PlaceOrderRequest
from app.models.bot_config import BotConfig
from app.models.order import Order
from app.models.bot_status import BotStatus
from app.services.trading_service import trading_service
from app.services.activity_log_service import activity_log_service
from app.services.telegram_service import telegram_service
from app.core.security import verify_token, check_ip_whitelist
from app.exceptions.error_code import ErrorCode
from app.exceptions.error_exception import ErrorException
from app.exceptions.logical_exception import ExchangeException, NotFoundException, BadRequestException
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/place-order")
async def place_order_direct(
    request: PlaceOrderRequest,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Đặt lệnh trực tiếp lên Binance (không qua webhook)
    
    Yêu cầu:
    - Bot config phải có API key/secret
    - Bot config phải active
    - Bot không được pause
    """
    try:
        # Get bot config
        config = db.query(BotConfig).filter(
            BotConfig.id == request.bot_config_id,
            BotConfig.is_active == True
        ).first()
        
        if not config:
            raise NotFoundException(
                message=f"Bot config {request.bot_config_id} not found or inactive"
            )
        
        # Check if bot is paused
        bot_status = db.query(BotStatus).filter(
            BotStatus.bot_config_id == config.id
        ).first()
        
        if bot_status and bot_status.is_paused:
            raise BadRequestException(
                message=f"Bot {config.name} is paused"
            )
        
        # Check API credentials
        if not config.api_key_encrypted or not config.api_secret_encrypted:
            raise BadRequestException(
                message="Bot config missing API credentials. Please add API key and secret."
            )
        
        # Use provided amount or config amount (if amount is 0 or None, use config amount)
        amount = request.amount if request.amount and request.amount > 0 else config.amount
        
        if not amount or amount <= 0:
            raise BadRequestException(
                message="Amount must be greater than 0. Please provide amount in request or configure it in bot config."
            )
        
        # Use provided symbol or config symbol
        symbol = request.symbol if request.symbol else config.symbol
        
        # Determine order type
        order_type = request.order_type
        price = request.price if order_type == "limit" else None
        
        if order_type == "limit" and not price:
            raise BadRequestException(
                message="Price is required for limit orders"
            )
        
        # Place order on exchange
        order_result = trading_service.place_order(
            config=config,
            side=request.side,
            amount=amount,
            price=price,
            order_type=order_type,
            symbol=symbol
        )
        
        if not order_result["success"]:
            error_msg = order_result.get("error")
            hint = order_result.get("hint")
            full_error = f"{error_msg}\n\n💡 {hint}" if hint else error_msg
            logger.error(f"Failed to place order: {full_error}")
            
            # Log error
            activity_log_service.log_activity(
                db=db,
                level="error",
                category="trading",
                message=full_error,
                bot_config_id=config.id,
                details=order_result
            )
            
            # Update bot status
            if bot_status:
                bot_status.failed_orders += 1
                bot_status.last_error = full_error
                db.commit()
            
            # Send Telegram notification
            if config.enable_notifications:
                telegram_service.send_error_alert(config.name, full_error)
            
            raise ExchangeException(
                message=error_msg,
                error_details=order_result,
                hint=hint
            )
        
        # Get order data
        order_data = order_result["order"]
        filled_price = order_result.get("filled_price") or order_data.get("price") or order_data.get("average")
        
        # Calculate SL/TP prices
        if filled_price:
            sl_tp = trading_service.calculate_sl_tp_prices(
                entry_price=filled_price,
                side=request.side,
                sl_percent=config.stop_loss_percent,
                tp_percent=config.take_profit_percent
            )
        else:
            sl_tp = {"stop_loss": None, "take_profit": None}

        # Place TP/SL orders on exchange (Binance Futures)
        tp_sl_result = None
        if (sl_tp["stop_loss"] or sl_tp["take_profit"]) and config.trading_mode == "futures":
            tp_sl_result = trading_service.place_tp_sl_orders(
                config=config,
                symbol=symbol,
                side=request.side,
                amount=amount,
                stop_loss_price=sl_tp["stop_loss"],
                take_profit_price=sl_tp["take_profit"]
            )
        
        # Create order record in DB
        db_order = Order(
            bot_config_id=config.id,
            exchange_order_id=order_result.get("exchange_order_id"),
            symbol=symbol,  # Use the symbol that was actually traded
            side=request.side,
            order_type=order_type,
            amount=amount,
            price=filled_price or price,
            leverage=config.leverage,
            status="filled" if order_result.get("filled_amount", 0) > 0 else "pending",
            filled_amount=order_result.get("filled_amount", amount),
            filled_price=filled_price,
            stop_loss_price=sl_tp["stop_loss"],
            take_profit_price=sl_tp["take_profit"],
            tp_levels=[tp for tp in (config.tp_levels or [])],
            trailing_enabled=config.enable_trailing,
            exchange=config.exchange,
            trading_mode=config.trading_mode,
            raw_data={
                "main_order": order_data,
                "tp_sl_result": tp_sl_result
            }
        )
        
        db.add(db_order)
        
        # Update bot status
        if bot_status:
            bot_status.total_orders += 1
            bot_status.successful_orders += 1
            bot_status.last_activity = db_order.created_at
            bot_status.is_running = True
            bot_status.health_status = "healthy"
        
        db.commit()
        db.refresh(db_order)
        
        # Log activity
        activity_log_service.log_activity(
            db=db,
            level="success",
            category="trading",
            message=f"Order placed directly: {request.side} {symbol} @ {filled_price or price}",
            bot_config_id=config.id,
            order_id=db_order.id
        )
        
        # Send Telegram notification
        if config.enable_notifications:
            telegram_service.send_order_notification({
                "symbol": symbol,
                "side": request.side,
                "amount": amount,
                "price": filled_price or price,
                "status": db_order.status
            })
        
        logger.info(f"Order placed directly: {db_order.id} - {symbol} - {request.side}")
        
        return {
            "status": "success",
            "order_id": db_order.id,
            "exchange_order_id": order_result.get("exchange_order_id"),
            "symbol": symbol,
            "side": request.side,
            "order_type": order_type,
            "amount": amount,
            "price": filled_price or price,
            "filled_price": filled_price,
            "stop_loss": sl_tp["stop_loss"],
            "take_profit": sl_tp["take_profit"],
            "order_status": db_order.status
        }
    
    except (HTTPException, ErrorException):
        raise
    except Exception as e:
        logger.error(f"Place order error: {e}", exc_info=True)
        activity_log_service.log_activity(
            db=db,
            level="error",
            category="trading",
            message=f"Place order error: {str(e)}",
            details={"request": request.dict()}
        )
        raise ErrorException(
            error_code=ErrorCode.UNDEFINED_ERROR,
            message=f"Internal server error: {str(e)}"
        )


@router.post("/close-order/{order_id}")
async def close_order(
    order_id: int,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Đóng lệnh (close position) trực tiếp
    """
    try:
        # Get order
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise NotFoundException(
                message=f"Order {order_id} not found"
            )
        
        # Get config
        config = db.query(BotConfig).filter(BotConfig.id == order.bot_config_id).first()
        if not config:
            raise NotFoundException(
                message="Bot config not found"
            )
        
        # Check if order is already closed
        if order.status in ["cancelled", "closed"]:
            raise BadRequestException(
                message=f"Order {order_id} is already {order.status}"
            )
        
        # Close position
        close_result = trading_service.close_position(config, order)
        
        if not close_result["success"]:
            raise ExchangeException(
                message=f"Failed to close order: {close_result.get('error')}",
                error_details=close_result
            )
        
        # Get PnL from exchange (Cách 2: Lấy từ sàn và lưu vào DB)
        # Ưu tiên dùng Binance Futures API nếu là futures và có exchange_order_id
        if config.trading_mode == "futures" and config.exchange.lower() == "binance" and order.exchange_order_id:
            pnl_result = trading_service.fetch_pnl_by_order_id_binance_futures(config, order)
            if pnl_result["success"]:
                pnl = pnl_result.get("pnl", 0.0)
                pnl_percent = pnl_result.get("pnl_percent", 0.0)
                close_price = close_result.get("close_price")
            else:
                # Fallback về cách cũ
                logger.warning(f"Binance Futures API failed, using close_result: {pnl_result.get('error')}")
                pnl = close_result.get("pnl", 0.0)
                pnl_percent = close_result.get("pnl_percent", 0.0)
                close_price = close_result.get("close_price")
        else:
            pnl = close_result.get("pnl", 0.0)
            pnl_percent = close_result.get("pnl_percent", 0.0)
            close_price = close_result.get("close_price")
        
        # Update order status and PnL
        from datetime import datetime
        order.status = "closed"
        order.closed_at = datetime.utcnow()
        order.pnl = pnl
        order.pnl_percent = pnl_percent
        
        # Update filled_price if we got close price and it's different
        if close_price and not order.filled_price:
            order.filled_price = close_price
        
        # Update bot status with PnL
        bot_status = db.query(BotStatus).filter(
            BotStatus.bot_config_id == config.id
        ).first()
        
        if bot_status:
            bot_status.total_pnl = (bot_status.total_pnl or 0.0) + pnl
        
        db.commit()
        
        # Log activity
        activity_log_service.log_activity(
            db=db,
            level="success",
            category="trading",
            message=f"Order closed: {order_id}",
            bot_config_id=config.id,
            order_id=order_id
        )
        
        return {
            "status": "success",
            "message": f"Order {order_id} closed successfully",
            "order_id": order_id,
            "close_order": close_result.get("order"),
            "pnl": pnl,
            "pnl_percent": pnl_percent,
            "close_price": close_price
        }
    
    except (HTTPException, ErrorException):
        raise
    except Exception as e:
        logger.error(f"Close order error: {e}", exc_info=True)
        raise ErrorException(
            error_code=ErrorCode.UNDEFINED_ERROR,
            message=f"Internal server error: {str(e)}"
        )


@router.post("/cancel-order/{order_id}")
async def cancel_order(
    order_id: int,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Cancel a pending order on the exchange"""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise NotFoundException(
                message=f"Order {order_id} not found"
            )

        if order.status != "pending":
            raise BadRequestException(
                message=f"Order {order_id} is not pending"
            )

        config = db.query(BotConfig).filter(BotConfig.id == order.bot_config_id).first()
        if not config:
            raise NotFoundException(
                message="Bot config not found"
            )

        if not order.exchange_order_id:
            raise BadRequestException(
                message="Order does not have exchange order ID"
            )

        cancel_result = trading_service.cancel_order(config, order)
        if not cancel_result["success"]:
            raise ExchangeException(
                message=cancel_result.get("error"),
                error_details=cancel_result
            )

        order.status = "cancelled"
        order.closed_at = datetime.utcnow()
        db.commit()

        activity_log_service.log_activity(
            db=db,
            level="info",
            category="trading",
            message=f"Order cancelled: {order_id}",
            bot_config_id=config.id,
            order_id=order_id
        )

        return {
            "status": "success",
            "message": f"Order {order_id} cancelled",
            "order_id": order_id,
            "exchange_order": cancel_result.get("order")
        }
    except (HTTPException, ErrorException):
        raise
    except Exception as e:
        logger.error(f"Cancel order error: {e}", exc_info=True)
        raise ErrorException(
            error_code=ErrorCode.UNDEFINED_ERROR,
            message=f"Internal server error: {str(e)}"
        )


@router.get("/symbols/{config_id}")
async def get_symbols(
    config_id: int,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách symbols từ exchange
    """
    try:
        # Get config
        config = db.query(BotConfig).filter(BotConfig.id == config_id).first()
        if not config:
            raise NotFoundException(
                message=f"Bot config {config_id} not found"
            )
        
        # Check API credentials
        if not config.api_key_encrypted or not config.api_secret_encrypted:
            raise BadRequestException(
                message="Bot config missing API credentials. Cannot fetch symbols."
            )
        
        # Get symbols from exchange
        result = trading_service.get_symbols(config)
        
        if not result["success"]:
            raise ExchangeException(
                message=result.get("error"),
                error_details=result
            )
        
        return {
            "symbols": result["symbols"],
            "count": result["count"],
            "exchange": config.exchange,
            "trading_mode": config.trading_mode
        }
    
    except (HTTPException, ErrorException):
        raise
    except Exception as e:
        logger.error(f"Get symbols error: {e}", exc_info=True)
        raise ErrorException(
            error_code=ErrorCode.UNDEFINED_ERROR,
            message=f"Internal server error: {str(e)}"
        )


@router.get("/check-order/{order_id}")
async def check_order_status(
    order_id: int,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Kiểm tra trạng thái lệnh trên Binance
    """
    try:
        # Get order
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise NotFoundException(
                message=f"Order {order_id} not found"
            )
        
        # Get config
        config = db.query(BotConfig).filter(BotConfig.id == order.bot_config_id).first()
        if not config:
            raise NotFoundException(
                message="Bot config not found"
            )
        
        if not order.exchange_order_id:
            raise BadRequestException(
                message="Order does not have exchange order ID"
            )
        
        # Check order status on exchange
        status_result = trading_service.check_order_status(config, order.exchange_order_id)
        
        if not status_result["success"]:
            raise ExchangeException(
                message=status_result.get("error"),
                error_details=status_result
            )
        
        # Update order in DB if status changed
        exchange_status = status_result.get("status")
        if exchange_status and exchange_status != order.status:
            order.status = exchange_status
            order.filled_amount = status_result.get("filled", order.filled_amount)
            db.commit()
        
        return {
            "order_id": order_id,
            "exchange_order_id": order.exchange_order_id,
            "status": status_result.get("status"),
            "filled": status_result.get("filled"),
            "remaining": status_result.get("remaining"),
            "order_data": status_result.get("order")
        }
    
    except (HTTPException, ErrorException):
        raise
    except Exception as e:
        logger.error(f"Check order error: {e}", exc_info=True)
        raise ErrorException(
            error_code=ErrorCode.UNDEFINED_ERROR,
            message=f"Internal server error: {str(e)}"
        )


@router.post("/refresh-pnl/{order_id}")
async def refresh_pnl(
    order_id: int,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Lấy lại PnL từ sàn và cập nhật vào database
    
    Endpoint này cho phép refresh PnL từ sàn cho một order cụ thể.
    Hữu ích khi:
    - Muốn cập nhật PnL real-time cho lệnh đang mở
    - Muốn lấy lại PnL chính xác từ sàn cho lệnh đã đóng
    """
    try:
        # Get order
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise NotFoundException(
                message=f"Order {order_id} not found"
            )
        
        # Get config
        config = db.query(BotConfig).filter(BotConfig.id == order.bot_config_id).first()
        if not config:
            raise NotFoundException(
                message="Bot config not found"
            )
        
        # Check API credentials
        if not config.api_key_encrypted or not config.api_secret_encrypted:
            raise BadRequestException(
                message="Bot config missing API credentials"
            )
        
        # Get PnL from exchange
        # Ưu tiên dùng Binance Futures API nếu là futures và có exchange_order_id
        if config.trading_mode == "futures" and config.exchange.lower() == "binance" and order.exchange_order_id:
            pnl_result = trading_service.fetch_pnl_by_order_id_binance_futures(config, order)
            # Nếu Binance API fail, fallback về cách cũ
            if not pnl_result["success"]:
                logger.warning(f"Binance Futures API failed, fallback to CCXT: {pnl_result.get('error')}")
                pnl_result = trading_service.get_pnl_from_exchange(config, order)
        else:
            pnl_result = trading_service.get_pnl_from_exchange(config, order)
        
        if not pnl_result["success"]:
            raise ExchangeException(
                message=pnl_result.get("error"),
                error_details=pnl_result
            )
        
        # Update PnL in database
        pnl = pnl_result.get("pnl", 0.0)
        pnl_percent = pnl_result.get("pnl_percent", 0.0)
        current_price = pnl_result.get("current_price")
        
        order.pnl = pnl
        order.pnl_percent = pnl_percent
        
        # Update bot status total PnL if order is closed
        if order.status == "closed":
            bot_status = db.query(BotStatus).filter(
                BotStatus.bot_config_id == config.id
            ).first()
            if bot_status:
                # Recalculate total PnL for closed orders
                closed_orders = db.query(Order).filter(
                    Order.bot_config_id == config.id,
                    Order.status == "closed"
                ).all()
                total_pnl = sum(o.pnl or 0.0 for o in closed_orders)
                bot_status.total_pnl = total_pnl
        
        db.commit()
        db.refresh(order)
        
        # Log activity
        activity_log_service.log_activity(
            db=db,
            level="info",
            category="trading",
            message=f"PnL refreshed from exchange: Order {order_id}, PnL={pnl}",
            bot_config_id=config.id,
            order_id=order_id
        )
        
        logger.info(f"PnL refreshed: Order {order_id}, PnL={pnl}, PnL%={pnl_percent}")
        
        return {
            "status": "success",
            "message": f"PnL refreshed for order {order_id}",
            "order_id": order_id,
            "pnl": pnl,
            "pnl_percent": pnl_percent,
            "current_price": current_price,
            "order_status": order.status
        }
    
    except (HTTPException, ErrorException):
        raise
    except Exception as e:
        logger.error(f"Refresh PnL error: {e}", exc_info=True)
        raise ErrorException(
            error_code=ErrorCode.UNDEFINED_ERROR,
            message=f"Internal server error: {str(e)}"
        )


@router.post("/place-order-pine")
async def place_order_pine_script(
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Đặt lệnh từ Pine Script (không cần JWT token)
    
    Endpoint này được thiết kế cho Pine Script, không yêu cầu JWT authentication.
    Bảo mật dựa trên IP whitelist (nếu bật).
    
    Yêu cầu:
    - Bot config phải có API key/secret
    - Bot config phải active
    - Bot không được pause
    - IP phải trong whitelist (nếu ENABLE_IP_WHITELIST=true)
    
    Hỗ trợ đầy đủ tính năng:
    - Custom amount
    - Custom price (limit order)
    - Custom symbol
    - Order type (market/limit)
    """
    # IP whitelist check
    client_ip = http_request.client.host
    forwarded_for = http_request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    
    if not check_ip_whitelist(client_ip):
        logger.warning(f"Pine Script API request from unauthorized IP: {client_ip}")
        raise ForbiddenException(message="IP address not allowed")
    
    # Log và parse request body
    try:
        body = await http_request.body()
        body_str = body.decode('utf-8')
        logger.info(f"Pine Script request from {client_ip}: {body_str}")
        
        # Try to parse as JSON
        try:
            body_json = json.loads(body_str)
        except json.JSONDecodeError:
            # If not JSON, might be plain text - try to parse as key=value format
            logger.warning(f"Request body is not valid JSON, attempting to parse as plain text: {body_str}")
            # If it's plain text, return error with helpful message
            raise ValidationException(
                message=f"Invalid JSON format. Expected JSON, got: {body_str[:100]}"
            )
        
        # Validate request using Pydantic
        request = PlaceOrderRequest(**body_json)
    except (HTTPException, ErrorException):
        raise
    except Exception as e:
        logger.error(f"Error parsing request body: {str(e)}")
        raise ValidationException(
            message=f"Invalid request format: {str(e)}"
        )
    
    try:
        # Get bot config
        config = db.query(BotConfig).filter(
            BotConfig.id == request.bot_config_id,
            BotConfig.is_active == True
        ).first()
        
        if not config:
            raise NotFoundException(
                message=f"Bot config {request.bot_config_id} not found or inactive"
            )
        
        # Check if bot is paused
        bot_status = db.query(BotStatus).filter(
            BotStatus.bot_config_id == config.id
        ).first()
        
        if bot_status and bot_status.is_paused:
            raise BadRequestException(
                message=f"Bot {config.name} is paused"
            )
        
        # Check API credentials
        if not config.api_key_encrypted or not config.api_secret_encrypted:
            raise BadRequestException(
                message="Bot config missing API credentials. Please add API key and secret."
            )
        
        # Use provided amount or config amount (if amount is 0 or None, use config amount)
        amount = request.amount if request.amount and request.amount > 0 else config.amount
        
        if not amount or amount <= 0:
            raise BadRequestException(
                message="Amount must be greater than 0. Please provide amount in request or configure it in bot config."
            )
        
        # Use provided symbol or config symbol
        symbol = request.symbol if request.symbol else config.symbol
        
        # Determine order type
        order_type = request.order_type
        price = request.price if order_type == "limit" else None
        
        if order_type == "limit" and not price:
            raise BadRequestException(
                message="Price is required for limit orders"
            )
        
        # Place order on exchange
        order_result = trading_service.place_order(
            config=config,
            side=request.side,
            amount=amount,
            price=price,
            order_type=order_type,
            symbol=symbol
        )
        
        if not order_result["success"]:
            error_msg = order_result.get("error")
            hint = order_result.get("hint")
            full_error = f"{error_msg}\n\n💡 {hint}" if hint else error_msg
            logger.error(f"Failed to place order: {full_error}")
            
            # Log error
            activity_log_service.log_activity(
                db=db,
                level="error",
                category="trading",
                message=full_error,
                bot_config_id=config.id,
                details=order_result
            )
            
            # Update bot status
            if bot_status:
                bot_status.failed_orders += 1
                bot_status.last_error = full_error
                db.commit()
            
            # Send Telegram notification
            if config.enable_notifications:
                telegram_service.send_error_alert(config.name, full_error)
            
            raise ExchangeException(
                message=error_msg,
                error_details=order_result,
                hint=hint
            )
        
        # Get order data
        order_data = order_result["order"]
        filled_price = order_result.get("filled_price") or order_data.get("price") or order_data.get("average")
        
        # Calculate SL/TP prices
        if filled_price:
            sl_tp = trading_service.calculate_sl_tp_prices(
                entry_price=filled_price,
                side=request.side,
                sl_percent=config.stop_loss_percent,
                tp_percent=config.take_profit_percent
            )
        else:
            sl_tp = {"stop_loss": None, "take_profit": None}
        
        # Place TP/SL orders on exchange (Binance Futures)
        tp_sl_result = None
        if (sl_tp["stop_loss"] or sl_tp["take_profit"]) and config.trading_mode == "futures":
            try:
                tp_sl_result = trading_service.place_tp_sl_orders(
                    config=config,
                    symbol=symbol,
                    side=request.side,
                    amount=amount,
                    stop_loss_price=sl_tp["stop_loss"],
                    take_profit_price=sl_tp["take_profit"]
                )
                logger.info(f"TP/SL orders placed on exchange for Pine Script order: {symbol}")
            except Exception as e:
                logger.warning(f"Failed to place TP/SL orders on exchange: {e}. Order still successful.")
                # Don't fail the main order if TP/SL fails
        
        # Create order record in DB
        db_order = Order(
            bot_config_id=config.id,
            exchange_order_id=order_result.get("exchange_order_id"),
            symbol=symbol,
            side=request.side,
            order_type=order_type,
            amount=amount,
            price=filled_price or price,
            leverage=config.leverage,
            status="filled" if order_result.get("filled_amount", 0) > 0 else "pending",
            filled_amount=order_result.get("filled_amount", amount),
            filled_price=filled_price,
            stop_loss_price=sl_tp["stop_loss"],
            take_profit_price=sl_tp["take_profit"],
            tp_levels=[tp for tp in (config.tp_levels or [])],
            trailing_enabled=config.enable_trailing,
            exchange=config.exchange,
            trading_mode=config.trading_mode,
            raw_data={
                "main_order": order_data,
                "tp_sl_result": tp_sl_result
            }
        )
        
        db.add(db_order)
        
        # Update bot status
        if bot_status:
            bot_status.total_orders += 1
            bot_status.successful_orders += 1
            bot_status.last_activity = db_order.created_at
            bot_status.is_running = True
            bot_status.health_status = "healthy"
        
        db.commit()
        db.refresh(db_order)
        
        # Log activity
        activity_log_service.log_activity(
            db=db,
            level="success",
            category="trading",
            message=f"Order placed from Pine Script: {request.side} {symbol} @ {filled_price or price}",
            bot_config_id=config.id,
            order_id=db_order.id,
            source_ip=client_ip
        )
        
        # Send Telegram notification
        if config.enable_notifications:
            telegram_service.send_order_notification({
                "symbol": symbol,
                "side": request.side,
                "amount": amount,
                "price": filled_price or price,
                "status": db_order.status
            })
        
        logger.info(f"Order placed from Pine Script: {db_order.id} - {symbol} - {request.side}")
        
        # Initialize trailing stop if enabled
        if config.enable_trailing and db_order.trailing_enabled:
            # Set initial trailing high price
            if filled_price:
                db_order.trailing_high_price = filled_price
                db.commit()
                logger.info(f"Trailing stop enabled for Pine Script order {db_order.id}. Initial high price: {filled_price}")
        
        return {
            "status": "success",
            "order_id": db_order.id,
            "exchange_order_id": order_result.get("exchange_order_id"),
            "symbol": symbol,
            "side": request.side,
            "order_type": order_type,
            "amount": amount,
            "price": filled_price or price,
            "filled_price": filled_price,
            "stop_loss": sl_tp["stop_loss"],
            "take_profit": sl_tp["take_profit"],
            "tp_sl_placed": tp_sl_result is not None and tp_sl_result.get("success", False),
            "trailing_enabled": config.enable_trailing,
            "order_status": db_order.status
        }
    
    except (HTTPException, ErrorException):
        raise
    except Exception as e:
        logger.error(f"Pine Script place order error: {e}", exc_info=True)
        activity_log_service.log_activity(
            db=db,
            level="error",
            category="trading",
            message=f"Pine Script place order error: {str(e)}",
            details={"request": request.dict()}
        )
        raise ErrorException(
            error_code=ErrorCode.UNDEFINED_ERROR,
            message=f"Internal server error: {str(e)}"
        )


from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from typing import Dict, Optional
import logging

from app.database import get_db
from app.models.bot_config import BotConfig
from app.models.order import Order
from app.models.bot_status import BotStatus
from app.services.trading_service import trading_service
from app.services.trailing_service import trailing_service
from app.services.telegram_service import telegram_service
from app.services.activity_log_service import activity_log_service
from app.core.security import check_ip_whitelist
from app.core.config import settings
from app.exceptions.error_code import ErrorCode
from app.exceptions.error_exception import ErrorException
from app.exceptions.logical_exception import ExchangeException, NotFoundException, BadRequestException, ForbiddenException

logger = logging.getLogger(__name__)

router = APIRouter()


def check_duplicate_order(db: Session, config_id: int, symbol: str) -> bool:
    """Check if there's already an open order for this config"""
    open_order = db.query(Order).filter(
        Order.bot_config_id == config_id,
        Order.symbol == symbol,
        Order.status.in_(["pending", "filled"])
    ).first()
    return open_order is not None


@router.post("/tradingview")
async def tradingview_webhook(
    request: Request,
    payload: Dict,
    db: Session = Depends(get_db)
):
    """
    TradingView webhook endpoint
    Reads configuration directly from DB when receiving alert
    """
    # IP whitelist check
    client_ip = request.client.host
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    
    if not check_ip_whitelist(client_ip):
        logger.warning(f"Webhook request from unauthorized IP: {client_ip}")
        raise ForbiddenException(message="IP address not allowed")
    
    try:
        # Extract webhook data
        symbol = payload.get("symbol") or payload.get("ticker")
        action = payload.get("action") or payload.get("side", "buy").lower()
        config_name = payload.get("config") or payload.get("bot_name")
        
        if not symbol:
            raise ValueError("Symbol/ticker is required")
        
        # Find bot config by name or symbol
        config = None
        if config_name:
            config = db.query(BotConfig).filter(
                BotConfig.name == config_name,
                BotConfig.is_active == True
            ).first()
        
        if not config:
            # Try to find by symbol
            config = db.query(BotConfig).filter(
                BotConfig.symbol == symbol,
                BotConfig.is_active == True
            ).first()
        
        if not config:
            error_msg = f"No active bot config found for symbol: {symbol}"
            logger.error(error_msg)
            activity_log_service.log_activity(
                db=db,
                level="error",
                category="webhook",
                message=error_msg,
                details=payload
            )
            raise NotFoundException(message=error_msg)
        
        # Check if bot is paused
        bot_status = db.query(BotStatus).filter(
            BotStatus.bot_config_id == config.id
        ).first()
        
        if bot_status and bot_status.is_paused:
            error_msg = f"Bot {config.name} is paused"
            logger.warning(error_msg)
            if config.enable_notifications:
                telegram_service.send_bot_paused_alert(config.name, "Bot is paused")
            raise BadRequestException(message=error_msg)
        
        # Check for duplicate orders
        if check_duplicate_order(db, config.id, symbol):
            error_msg = f"Duplicate order detected for {symbol}"
            logger.warning(error_msg)
            activity_log_service.log_activity(
                db=db,
                level="warning",
                category="webhook",
                message=error_msg,
                bot_config_id=config.id
            )
            return {
                "status": "skipped",
                "message": error_msg
            }
        
        # Determine order side
        side = "buy" if action in ["buy", "long", "enter"] else "sell"
        
        # Normalize symbol from TradingView format to Binance format
        symbol_normalized = trading_service.normalize_symbol(symbol, config.trading_mode)
        
        # Place order
        order_result = trading_service.place_order(
            config=config,
            side=side,
            amount=config.amount,
            order_type="market",
            symbol=symbol_normalized
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
                category="webhook",
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
        
        # Create order record
        order_data = order_result["order"]
        filled_price = order_result.get("filled_price") or order_data.get("price") or order_data.get("average")
        
        # Calculate SL/TP prices
        if filled_price:
            sl_tp = trading_service.calculate_sl_tp_prices(
                entry_price=filled_price,
                side=side,
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
                    symbol=symbol_normalized,
                    side=side,
                    amount=config.amount,
                    stop_loss_price=sl_tp["stop_loss"],
                    take_profit_price=sl_tp["take_profit"]
                )
                logger.info(f"TP/SL orders placed on exchange for order: {symbol_normalized}")
            except Exception as e:
                logger.warning(f"Failed to place TP/SL orders on exchange: {e}. Order still successful.")
                # Don't fail the main order if TP/SL fails
        
        # Create order in DB
        db_order = Order(
            bot_config_id=config.id,
            exchange_order_id=order_result.get("exchange_order_id"),
            symbol=symbol_normalized,  # Use normalized symbol
            side=side,
            order_type="market",
            amount=config.amount,
            price=filled_price,
            leverage=config.leverage,
            status="filled" if order_result.get("filled_amount", 0) > 0 else "pending",
            filled_amount=order_result.get("filled_amount", config.amount),
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
            category="webhook",
            message=f"Order placed: {side} {symbol} @ {filled_price}",
            bot_config_id=config.id,
            order_id=db_order.id,
            source_ip=client_ip
        )
        
        # Send Telegram notification
        if config.enable_notifications:
            telegram_service.send_order_notification({
                "symbol": symbol,
                "side": side,
                "amount": config.amount,
                "price": filled_price,
                "status": db_order.status
            })
        
        logger.info(f"Order placed successfully: {db_order.id} - {symbol_normalized} - {side}")
        
        # Initialize trailing stop if enabled
        if config.enable_trailing and db_order.trailing_enabled:
            # Set initial trailing high price
            if filled_price:
                db_order.trailing_high_price = filled_price
                db.commit()
                logger.info(f"Trailing stop enabled for order {db_order.id}. Initial high price: {filled_price}")
        
        return {
            "status": "success",
            "order_id": db_order.id,
            "symbol": symbol_normalized,
            "side": side,
            "amount": config.amount,
            "price": filled_price,
            "stop_loss": sl_tp["stop_loss"],
            "take_profit": sl_tp["take_profit"],
            "tp_sl_placed": tp_sl_result is not None and tp_sl_result.get("success", False),
            "trailing_enabled": config.enable_trailing
        }
    
    except ErrorException:
        raise
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        activity_log_service.log_activity(
            db=db,
            level="error",
            category="webhook",
            message=f"Webhook error: {str(e)}",
            details={"payload": payload}
        )
        raise ErrorException(
            error_code=ErrorCode.UNDEFINED_ERROR,
            message=f"Internal server error: {str(e)}"
        )


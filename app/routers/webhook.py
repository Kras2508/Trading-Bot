from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from typing import Dict, Optional
import logging
from datetime import datetime

from app.database import get_db
from app.models.bot_config import BotConfig
from app.models.order import Order
from app.models.bot_status import BotStatus
from app.services.trading_service import trading_service
from app.services.trailing_service import trailing_service
from app.services.telegram_service import telegram_service
from app.services.activity_log_service import activity_log_service
from app.core.security import check_ip_whitelist, verify_token
from app.core.config import settings
from app.exceptions.error_code import ErrorCode
from app.exceptions.error_exception import ErrorException
from app.exceptions.logical_exception import ExchangeException, NotFoundException, BadRequestException, ForbiddenException
from app.models.system_setting import SystemSetting
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class SystemSettingUpdate(BaseModel):
    webhook_passphrase: Optional[str] = None
    enable_ip_whitelist: Optional[bool] = None
    allowed_ips: Optional[str] = None


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
def check_ip_whitelist_db(client_ip: str, db: Session) -> bool:
    sys_setting = db.query(SystemSetting).first()
    if not sys_setting:
        return True
    if not sys_setting.enable_ip_whitelist:
        return True
    
    allowed_ips = [ip.strip() for ip in sys_setting.allowed_ips.split(",") if ip.strip()]
    if not allowed_ips:
        return True
        
    return client_ip in allowed_ips


async def execute_webhook_signal(payload: Dict, client_ip: str, db: Session, simulate_success: bool = False):
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
        
        # Normalize symbol from TradingView format to Binance format
        symbol_normalized = trading_service.normalize_symbol(symbol, config.trading_mode)
        
        # Determine order side
        side = "buy" if action in ["buy", "long", "enter"] else "sell"
        
        # Check if there is an open position in our DB
        open_order = db.query(Order).filter(
            Order.bot_config_id == config.id,
            Order.symbol == symbol_normalized,
            Order.status.in_(["pending", "filled"])
        ).first()
        
        if open_order:
            # Check if this signal is an exit or counter-signal
            is_exit_signal = action in ["close", "exit"]
            is_counter_signal = open_order.side != side
            
            if is_exit_signal or is_counter_signal:
                logger.info(f"Closing existing position for bot {config.name} on symbol {symbol_normalized}")
                pnl = 0.0
                pnl_percent = 0.0
                close_price = None
                
                if simulate_success:
                    # Get current simulated price
                    try:
                        import ccxt
                        ex_class = getattr(ccxt, config.exchange.lower())
                        ex = ex_class()
                        ticker = ex.fetch_ticker(symbol_normalized)
                        close_price = ticker.get("last") or ticker.get("close") or 1.0
                    except Exception:
                        close_price = open_order.filled_price or 1.0
                    
                    if open_order.filled_price and close_price:
                        if open_order.side == "buy":
                            pnl = (close_price - open_order.filled_price) * open_order.filled_amount * config.leverage
                        else:
                            pnl = (open_order.filled_price - close_price) * open_order.filled_amount * config.leverage
                        pnl_percent = (pnl / (open_order.filled_price * open_order.filled_amount)) * 100 if open_order.filled_price and open_order.filled_amount else 0.0
                else:
                    # Live trading close position
                    close_res = trading_service.close_position(config, open_order)
                    if not close_res["success"]:
                        error_msg = f"Failed to close existing position: {close_res.get('error')}"
                        logger.error(error_msg)
                        activity_log_service.log_activity(
                            db=db,
                            level="error",
                            category="webhook",
                            message=error_msg,
                            bot_config_id=config.id,
                            details=close_res
                        )
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=error_msg
                        )
                    pnl = close_res.get("pnl", 0.0)
                    pnl_percent = close_res.get("pnl_percent", 0.0)
                
                # Update DB
                open_order.status = "closed"
                open_order.closed_at = datetime.utcnow()
                open_order.pnl = pnl
                open_order.pnl_percent = pnl_percent
                
                if bot_status:
                    bot_status.total_pnl = (bot_status.total_pnl or 0.0) + pnl
                db.commit()
                
                close_msg = f"Closed position for {symbol_normalized} via webhook. PnL={pnl:.2f}"
                activity_log_service.log_activity(
                    db=db,
                    level="info",
                    category="webhook",
                    message=close_msg,
                    bot_config_id=config.id,
                    order_id=open_order.id
                )
                
                # Telegram alert
                if config.enable_notifications:
                    try:
                        telegram_service.send_message(
                            f"<b>[BOT CLOSE]</b> {config.name}\n"
                            f"Symbol: {symbol_normalized}\n"
                            f"Side: {open_order.side.upper()}\n"
                            f"PnL: {pnl:.2f} ({pnl_percent:.2f}%)"
                        )
                    except Exception as tel_err:
                        logger.error(f"Telegram notification failed: {tel_err}")
                
                # If explicit close action, we stop here
                if is_exit_signal:
                    return {
                        "status": "closed",
                        "message": f"Successfully closed position for {symbol_normalized}",
                        "pnl": pnl,
                        "pnl_percent": pnl_percent
                    }
            else:
                # Same side and not close action -> duplicate signal
                error_msg = f"Duplicate order detected for {symbol_normalized} (already {open_order.side.upper()} open)"
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
        else:
            # No position open, but request is to close/exit -> nothing to do
            if action in ["close", "exit"]:
                msg = f"Close request received for {symbol_normalized} but no open position found."
                logger.warning(msg)
                activity_log_service.log_activity(
                    db=db,
                    level="warning",
                    category="webhook",
                    message=msg,
                    bot_config_id=config.id
                )
                return {
                    "status": "skipped",
                    "message": msg
                }
        
        # Place order
        if simulate_success:
            import time
            try:
                # Try to fetch current price using public ccxt client without key
                import ccxt
                ex_class = getattr(ccxt, config.exchange.lower())
                ex = ex_class()
                ticker = ex.fetch_ticker(symbol_normalized)
                filled_price = ticker.get("last") or ticker.get("close") or 1.0
            except Exception as e:
                logger.warning(f"Failed to fetch simulated ticker price: {e}")
                filled_price = 1.0
            
            order_result = {
                "success": True,
                "order": {
                    "id": f"sim_{int(time.time())}",
                    "price": filled_price,
                    "average": filled_price,
                    "filled": config.amount,
                    "status": "closed",
                    "symbol": symbol_normalized,
                    "side": side,
                    "type": "market"
                },
                "exchange_order_id": f"sim_{int(time.time())}",
                "filled_price": filled_price,
                "filled_amount": config.amount
            }
        else:
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
        if (sl_tp["stop_loss"] or sl_tp["take_profit"]) and config.trading_mode == "futures" and not simulate_success:
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
    
    if not check_ip_whitelist_db(client_ip, db):
        logger.warning(f"Webhook request from unauthorized IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="IP address not allowed"
        )
    
    # Webhook Passphrase check
    sys_setting = db.query(SystemSetting).first()
    passphrase = sys_setting.webhook_passphrase if sys_setting else settings.WEBHOOK_PASSPHRASE
    
    if passphrase:
        payload_passphrase = payload.get("passphrase")
        if payload_passphrase != passphrase:
            logger.warning("Webhook request failed: Invalid or missing passphrase")
            activity_log_service.log_activity(
                db=db,
                level="error",
                category="webhook",
                message="Unauthorized webhook request: Invalid passphrase",
                details={"client_ip": client_ip}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing webhook passphrase"
            )
    
    return await execute_webhook_signal(payload, client_ip, db)


@router.post("/test-trigger")
async def test_webhook_trigger(
    request: Request,
    payload: Dict,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Simulate a TradingView webhook call for testing purposes (authenticated via JWT)
    Bypasses the IP Whitelist filter, but still enforces Passphrase check.
    """
    client_ip = request.client.host
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
        
    sys_setting = db.query(SystemSetting).first()
    passphrase = sys_setting.webhook_passphrase if sys_setting else settings.WEBHOOK_PASSPHRASE
    
    if passphrase:
        payload_passphrase = payload.get("passphrase")
        if payload_passphrase != passphrase:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing webhook passphrase"
            )
            
    simulate_success = payload.get("simulate_success", False)
    return await execute_webhook_signal(payload, client_ip, db, simulate_success=simulate_success)


@router.get("/info")
async def get_webhook_info(
    request: Request,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Get Webhook connection info and passphrase
    """
    base_url = str(request.base_url).rstrip("/")
    webhook_url = f"{base_url}/api/webhook/tradingview"
    
    # Official TradingView IPs
    tradingview_ips = [
        "52.89.214.238",
        "34.212.75.30",
        "54.112.49.227",
        "54.218.53.128",
        "3.220.172.38",
        "3.224.195.42",
        "34.200.222.167"
    ]
    
    # Load from DB
    sys_setting = db.query(SystemSetting).first()
    passphrase = sys_setting.webhook_passphrase if sys_setting else settings.WEBHOOK_PASSPHRASE
    passphrase_required = bool(passphrase)
    ip_whitelist_enabled = sys_setting.enable_ip_whitelist if sys_setting else settings.ENABLE_IP_WHITELIST
    allowed_ips = sys_setting.allowed_ips if sys_setting else ",".join(settings.ALLOWED_IPS)
    
    return {
        "webhook_url": webhook_url,
        "passphrase": passphrase,
        "passphrase_required": passphrase_required,
        "tradingview_ips": tradingview_ips,
        "ip_whitelist_enabled": ip_whitelist_enabled,
        "allowed_ips": allowed_ips
    }


@router.get("/settings")
async def get_webhook_settings(
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get active webhook security settings from DB"""
    sys_setting = db.query(SystemSetting).first()
    if not sys_setting:
        return {
            "webhook_passphrase": settings.WEBHOOK_PASSPHRASE,
            "enable_ip_whitelist": settings.ENABLE_IP_WHITELIST,
            "allowed_ips": ",".join(settings.ALLOWED_IPS) if isinstance(settings.ALLOWED_IPS, list) else str(settings.ALLOWED_IPS)
        }
    return {
        "webhook_passphrase": sys_setting.webhook_passphrase,
        "enable_ip_whitelist": sys_setting.enable_ip_whitelist,
        "allowed_ips": sys_setting.allowed_ips
    }


@router.post("/settings")
async def update_webhook_settings(
    data: SystemSettingUpdate,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Update webhook security settings in DB"""
    sys_setting = db.query(SystemSetting).first()
    if not sys_setting:
        sys_setting = SystemSetting(id=1)
        db.add(sys_setting)
        
    if data.webhook_passphrase is not None:
        sys_setting.webhook_passphrase = data.webhook_passphrase
    if data.enable_ip_whitelist is not None:
        sys_setting.enable_ip_whitelist = data.enable_ip_whitelist
    if data.allowed_ips is not None:
        sys_setting.allowed_ips = data.allowed_ips
        
    db.commit()
    db.refresh(sys_setting)
    
    activity_log_service.log_activity(
        db=db,
        level="info",
        category="system",
        message="System webhook security settings updated"
    )
    
    return {
        "status": "success",
        "webhook_passphrase": sys_setting.webhook_passphrase,
        "enable_ip_whitelist": sys_setting.enable_ip_whitelist,
        "allowed_ips": sys_setting.allowed_ips
    }


import asyncio
import logging
from datetime import datetime
import ccxt

from app.database import SessionLocal
from app.models.order import Order
from app.models.bot_config import BotConfig
from app.models.bot_status import BotStatus
from app.services.trading_service import trading_service
from app.services.activity_log_service import activity_log_service

logger = logging.getLogger(__name__)

async def run_order_sync_loop():
    """
    Background worker loop to periodically sync order status with the exchange.
    Runs every 30 seconds.
    Supports both simulated paper trading and real live trading.
    """
    logger.info("Starting background order status synchronization loop...")
    while True:
        try:
            await asyncio.sleep(30)
            
            db = SessionLocal()
            try:
                # Query all active orders in database
                active_orders = db.query(Order).filter(Order.status.in_(["pending", "filled"])).all()
                if not active_orders:
                    continue
                
                for order in active_orders:
                    # Load bot config
                    config = db.query(BotConfig).filter(BotConfig.id == order.bot_config_id).first()
                    if not config or not config.is_active:
                        continue
                    
                    # ----------------------------------------------------
                    # CASE A: Simulated Paper Trading Lệnh Giả Lập
                    # ----------------------------------------------------
                    if order.exchange_order_id and order.exchange_order_id.startswith("sim_"):
                        # If futures, simulate SL/TP triggers based on ticker price
                        if config.trading_mode == "futures" and (order.stop_loss_price or order.take_profit_price):
                            try:
                                ex_class = getattr(ccxt, config.exchange.lower())
                                ex = ex_class()
                                symbol_norm = trading_service.normalize_symbol(order.symbol, config.trading_mode)
                                ticker = ex.fetch_ticker(symbol_norm)
                                current_price = ticker.get("last") or ticker.get("close")
                                
                                if current_price:
                                    is_triggered = False
                                    reason = ""
                                    if order.side == "buy":  # Long position
                                        if order.stop_loss_price and current_price <= order.stop_loss_price:
                                            is_triggered = True
                                            reason = "Stop Loss"
                                        elif order.take_profit_price and current_price >= order.take_profit_price:
                                            is_triggered = True
                                            reason = "Take Profit"
                                    else:  # Short position
                                        if order.stop_loss_price and current_price >= order.stop_loss_price:
                                            is_triggered = True
                                            reason = "Stop Loss"
                                        elif order.take_profit_price and current_price <= order.take_profit_price:
                                            is_triggered = True
                                            reason = "Take Profit"
                                    
                                    if is_triggered:
                                        # Calculate simulated PnL
                                        pnl = 0.0
                                        if order.filled_price:
                                            if order.side == "buy":
                                                pnl = (current_price - order.filled_price) * order.filled_amount * config.leverage
                                            else:
                                                pnl = (order.filled_price - current_price) * order.filled_amount * config.leverage
                                        
                                        pnl_percent = (pnl / (order.filled_price * order.filled_amount)) * 100 if order.filled_price and order.filled_amount else 0.0
                                        
                                        # Close order in database
                                        order.status = "closed"
                                        order.closed_at = datetime.utcnow()
                                        order.pnl = pnl
                                        order.pnl_percent = pnl_percent
                                        
                                        # Update Bot Status total PnL
                                        bot_status = db.query(BotStatus).filter(BotStatus.bot_config_id == config.id).first()
                                        if bot_status:
                                            bot_status.total_pnl = (bot_status.total_pnl or 0.0) + pnl
                                        
                                        db.commit()
                                        
                                        activity_log_service.log_activity(
                                            db=db,
                                            level="info",
                                            category="trading",
                                            message=f"Simulated position closed: {order.symbol} hit {reason} at price {current_price}. PnL={pnl:.2f}",
                                            bot_config_id=config.id,
                                            order_id=order.id
                                        )
                                        logger.info(f"Simulated position hit {reason} for order {order.id}. PnL: {pnl}")
                            except Exception as sim_err:
                                logger.error(f"Error checking simulated SL/TP for order {order.id}: {sim_err}")
                        continue
                    
                    # ----------------------------------------------------
                    # CASE B: Real Live Trading Lệnh Thật Trên Sàn
                    # ----------------------------------------------------
                    # Verify API credentials exist
                    if not config.api_key_encrypted or not config.api_secret_encrypted:
                        continue
                    
                    if config.trading_mode == "futures":
                        # For futures, check if position has been closed on exchange
                        try:
                            exchange = trading_service.get_exchange(config)
                            symbol_norm = trading_service.normalize_symbol(order.symbol, config.trading_mode)
                            positions = exchange.fetch_positions([symbol_norm])
                            
                            for pos in positions:
                                if pos.get("symbol") == symbol_norm:
                                    contracts = pos.get("contracts", 0) or pos.get("positionAmt", 0)
                                    # If size is zero, position is closed
                                    if float(contracts) == 0:
                                        logger.info(f"Background Order Sync: Futures position closed on exchange for order {order.id}")
                                        
                                        pnl = 0.0
                                        pnl_percent = 0.0
                                        
                                        # Fetch realized PnL from Binance
                                        pnl_result = trading_service.fetch_pnl_by_order_id_binance_futures(config, order)
                                        if pnl_result["success"]:
                                            pnl = pnl_result.get("pnl", 0.0)
                                            pnl_percent = pnl_result.get("pnl_percent", 0.0)
                                        else:
                                            # Fallback manual calculation based on current ticker price
                                            try:
                                                ticker = exchange.fetch_ticker(symbol_norm)
                                                close_price = ticker.get("last") or ticker.get("close")
                                                if order.filled_price and close_price:
                                                    if order.side == "buy":
                                                        pnl = (close_price - order.filled_price) * order.filled_amount * config.leverage
                                                    else:
                                                        pnl = (order.filled_price - close_price) * order.filled_amount * config.leverage
                                                    pnl_percent = (pnl / (order.filled_price * order.filled_amount)) * 100
                                            except Exception as tick_err:
                                                logger.warning(f"Failed fallback ticker PnL calc: {tick_err}")
                                        
                                        # Update order in DB
                                        order.status = "closed"
                                        order.closed_at = datetime.utcnow()
                                        order.pnl = pnl
                                        order.pnl_percent = pnl_percent
                                        
                                        # Update bot status PnL
                                        bot_status = db.query(BotStatus).filter(BotStatus.bot_config_id == config.id).first()
                                        if bot_status:
                                            bot_status.total_pnl = (bot_status.total_pnl or 0.0) + pnl
                                        
                                        db.commit()
                                        
                                        activity_log_service.log_activity(
                                            db=db,
                                            level="info",
                                            category="trading",
                                            message=f"Order status synced to closed in background (Position closed on exchange). PnL={pnl:.2f}",
                                            bot_config_id=config.id,
                                            order_id=order.id
                                        )
                                    break
                        except Exception as fut_err:
                            logger.error(f"Error checking futures position in background loop: {fut_err}")
                    
                    else:
                        # For spot, check actual order status on exchange
                        try:
                            status_result = trading_service.check_order_status(config, order.exchange_order_id)
                            if status_result["success"]:
                                exchange_status = status_result.get("status")
                                if exchange_status and exchange_status != order.status:
                                    order.status = exchange_status
                                    order.filled_amount = status_result.get("filled", order.filled_amount)
                                    db.commit()
                                    
                                    activity_log_service.log_activity(
                                        db=db,
                                        level="info",
                                        category="trading",
                                        message=f"Spot order status synced to {exchange_status} in background",
                                        bot_config_id=config.id,
                                        order_id=order.id
                                    )
                                    logger.info(f"Background Order Sync: Spot order {order.id} status updated to {exchange_status}")
                        except Exception as spot_err:
                            logger.error(f"Error checking spot order in background loop: {spot_err}")
                            
            except Exception as loop_db_err:
                logger.error(f"Background worker database operation error: {loop_db_err}", exc_info=True)
            finally:
                db.close()
                
        except asyncio.CancelledError:
            logger.info("Background order sync loop cancelled")
            break
        except Exception as main_err:
            logger.error(f"Background order sync main loop error: {main_err}", exc_info=True)
            await asyncio.sleep(5)

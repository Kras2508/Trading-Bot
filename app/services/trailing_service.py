import logging
from typing import Optional
from app.models.order import Order
from app.models.bot_config import BotConfig
from app.services.trading_service import trading_service
import ccxt

logger = logging.getLogger(__name__)


class TrailingService:
    """Service for managing trailing stops"""
    
    def calculate_atr(self, exchange: ccxt.Exchange, symbol: str, period: int = 14) -> Optional[float]:
        """Calculate Average True Range (ATR)"""
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1d', limit=period + 1)
            if len(ohlcv) < period + 1:
                return None
            
            true_ranges = []
            for i in range(1, len(ohlcv)):
                high = ohlcv[i][2]
                low = ohlcv[i][3]
                prev_close = ohlcv[i-1][4]
                
                tr1 = high - low
                tr2 = abs(high - prev_close)
                tr3 = abs(low - prev_close)
                true_ranges.append(max(tr1, tr2, tr3))
            
            atr = sum(true_ranges) / len(true_ranges)
            return atr
        except Exception as e:
            logger.error(f"Failed to calculate ATR: {e}")
            return None
    
    def update_trailing_stop(
        self,
        order: Order,
        config: BotConfig,
        current_price: float
    ) -> Optional[float]:
        """Update trailing stop price"""
        if not config.enable_trailing or not order.trailing_enabled:
            return None
        
        if not order.filled_price:
            return None
        
        # Update highest price reached
        if order.side.lower() == "buy":
            if not order.trailing_high_price or current_price > order.trailing_high_price:
                order.trailing_high_price = current_price
        else:  # sell
            if not order.trailing_high_price or current_price < order.trailing_high_price:
                order.trailing_high_price = current_price
        
        # Calculate trailing stop
        if config.trailing_type == "percent":
            if not config.trailing_percent:
                return None
            
            trailing_stop = trading_service.calculate_trailing_stop(
                current_price,
                order.trailing_high_price,
                config.trailing_percent,
                order.side
            )
        elif config.trailing_type == "atr":
            if not config.trailing_atr_multiplier:
                return None
            
            try:
                exchange = trading_service.get_exchange(config)
                atr = self.calculate_atr(exchange, config.symbol, config.trailing_atr_period)
                if not atr:
                    return None
                
                trailing_distance = atr * config.trailing_atr_multiplier
                
                if order.side.lower() == "buy":
                    trailing_stop = order.trailing_high_price - trailing_distance
                else:  # sell
                    trailing_stop = order.trailing_high_price + trailing_distance
            except Exception as e:
                logger.error(f"Failed to calculate ATR-based trailing: {e}")
                return None
        else:
            return None
        
        # Update trailing stop price
        order.trailing_stop_price = trailing_stop
        
        return trailing_stop
    
    def check_trailing_stop_triggered(
        self,
        order: Order,
        current_price: float
    ) -> bool:
        """Check if trailing stop is triggered"""
        if not order.trailing_stop_price:
            return False
        
        if order.side.lower() == "buy":
            # Long position: stop loss if price drops below trailing stop
            return current_price <= order.trailing_stop_price
        else:  # sell
            # Short position: stop loss if price rises above trailing stop
            return current_price >= order.trailing_stop_price


trailing_service = TrailingService()


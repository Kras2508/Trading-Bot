import logging
import ccxt
import requests
import hmac
import hashlib
import time
from typing import Optional, Dict, List
from app.core.security import decrypt_data
from app.models.bot_config import BotConfig
from app.models.order import Order
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class TradingService:
    """Service for executing trades"""
    
    def __init__(self):
        self.exchanges = {}  # Cache for exchange instances
    
    def normalize_symbol(self, symbol: str, trading_mode: str = "spot") -> str:
        """
        Convert symbol from TradingView format to Binance format
        
        Examples:
        - BTC.D -> BTCUSDT (futures)
        - BTC/USDT -> BTCUSDT
        - BTCUSDT -> BTCUSDT (no change)
        - ETH.D -> ETHUSDT (futures)
        """
        if not symbol:
            return symbol
        
        symbol = symbol.strip().upper()
        
        # If already in Binance format (no dots, no slashes), return as is
        if '/' not in symbol and '.' not in symbol:
            return symbol
        
        # Handle TradingView futures format: BTC.D -> BTCUSDT
        if symbol.endswith('.D'):
            base = symbol[:-2]  # Remove .D
            return f"{base}USDT"
        
        # Handle slash format: BTC/USDT -> BTCUSDT
        if '/' in symbol:
            parts = symbol.split('/')
            if len(parts) == 2:
                base = parts[0]
                quote = parts[1]
                return f"{base}{quote}"
        
        # If we can't convert, return original (will fail with clear error)
        logger.warning(f"Could not normalize symbol format: {symbol}, returning as-is")
        return symbol

    def _is_timestamp_error(self, error_message: str) -> bool:
        """Check if an error is related to exchange timestamp drift."""
        error_text = (error_message or "").lower()
        return (
            "timestamp" in error_text
            or "-1021" in error_text
            or "recvwindow" in error_text
        )

    def _sync_exchange_time(self, exchange: ccxt.Exchange) -> None:
        """Force a fresh time-difference sync with the exchange server."""
        try:
            if hasattr(exchange, "load_time_difference"):
                exchange.load_time_difference()
                return

            if hasattr(exchange, "fetch_time"):
                server_time = exchange.fetch_time()
                if isinstance(server_time, (int, float)):
                    local_time = exchange.milliseconds()
                    exchange.options["timeDifference"] = local_time - int(server_time)
        except Exception as e:
            logger.warning(f"Could not sync exchange time difference: {e}")
    
    def get_exchange(self, config: BotConfig) -> ccxt.Exchange:
        """Get or create exchange instance"""
        exchange_name = config.exchange.lower()
        cache_key = f"{exchange_name}_{config.id}"
        
        if cache_key not in self.exchanges:
            exchange_class = getattr(ccxt, exchange_name)
            
            # Get API credentials
            api_key = None
            api_secret = None
            if config.api_key_encrypted and config.api_secret_encrypted:
                try:
                    api_key = decrypt_data(config.api_key_encrypted)
                    api_secret = decrypt_data(config.api_secret_encrypted)
                except Exception as e:
                    logger.error(f"Failed to decrypt API credentials: {e}")
                    raise
            
            exchange_params = {
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {
                    'adjustForTimeDifference': True,  # Auto-adjust timestamp
                    'recvWindow': 10000,              # More tolerant for network jitter
                }
            }
            
            if config.trading_mode == 'futures':
                exchange_params['options']['defaultType'] = 'future'
            
            self.exchanges[cache_key] = exchange_class(exchange_params)
        
        return self.exchanges[cache_key]
    
    def place_order(
        self,
        config: BotConfig,
        side: str,
        amount: float,
        price: Optional[float] = None,
        order_type: str = "market",
        symbol: Optional[str] = None
    ) -> Dict:
        """Place an order on the exchange"""
        try:
            exchange = self.get_exchange(config)
            symbol = symbol or config.symbol  # Use provided symbol or fallback to config symbol
            
            # Normalize symbol from TradingView format to Binance format
            symbol = self.normalize_symbol(symbol, config.trading_mode)
            logger.info(f"Normalized symbol: {symbol} (trading_mode: {config.trading_mode})")

            # Always re-sync time difference before signed requests.
            self._sync_exchange_time(exchange)
            
            if config.trading_mode == 'futures' and config.leverage > 1:
                # Set leverage for futures
                try:
                    exchange.set_leverage(config.leverage, symbol)
                except Exception as e:
                    logger.warning(f"Failed to set leverage: {e}")
            
            # Place order with retry for timestamp errors
            max_retries = 2
            retry_count = 0
            last_error = None
            
            while retry_count <= max_retries:
                try:
                    # Place order
                    if order_type == "market":
                        order = exchange.create_market_order(symbol, side, amount)
                    elif order_type == "limit":
                        if not price:
                            raise ValueError("Price required for limit order")
                        order = exchange.create_limit_order(symbol, side, amount, price)
                    else:
                        raise ValueError(f"Unsupported order type: {order_type}")
                    
                    logger.info(f"Order placed: {order}")
                    return {
                        "success": True,
                        "order": order,
                        "exchange_order_id": order.get("id"),
                        "filled_price": order.get("price") or order.get("average"),
                        "filled_amount": order.get("filled", amount)
                    }
                except Exception as e:
                    error_str = str(e)
                    last_error = e
                    
                    # Check if it's a timestamp error
                    if self._is_timestamp_error(error_str):
                        retry_count += 1
                        if retry_count <= max_retries:
                            logger.warning(f"Timestamp error detected (attempt {retry_count}/{max_retries}). Retrying...")
                            self._sync_exchange_time(exchange)
                            time.sleep(0.5 * retry_count)
                            continue
                    
                    # If not timestamp error or max retries reached, break
                    break
            
            # If we get here, all retries failed
            logger.error(f"Failed to place order after {retry_count} attempts: {last_error}")
            raw_error = str(last_error)
            hint = None
            if self._is_timestamp_error(raw_error):
                hint = (
                    "Hệ thống đã tự retry và sync thời gian với Binance nhưng vẫn thất bại. "
                    "Vui lòng sync thời gian máy tính bằng script FIX_TIMESTAMP_BINANCE.bat (Run as Administrator), "
                    "sau đó restart backend và thử lại."
                )
            
            return {
                "success": False,
                "error": raw_error,
                "hint": hint
            }
        except Exception as e:
            logger.error(f"Failed to place order (unexpected): {e}", exc_info=True)
            raw_error = str(e)
            hint = None
            if self._is_timestamp_error(raw_error):
                hint = (
                    "Hệ thống đã tự retry và sync thời gian với Binance nhưng vẫn thất bại. "
                    "Vui lòng sync thời gian máy tính bằng script FIX_TIMESTAMP_BINANCE.bat (Run as Administrator), "
                    "sau đó restart backend và thử lại."
                )
            return {
                "success": False,
                "error": raw_error,
                "hint": hint
            }

    def cancel_order(self, config: BotConfig, order: Order) -> Dict:
        """Cancel an existing order on the exchange"""
        try:
            exchange = self.get_exchange(config)
            symbol = self.normalize_symbol(order.symbol, config.trading_mode)

            self._sync_exchange_time(exchange)
            result = exchange.cancel_order(order.exchange_order_id, symbol)

            return {
                "success": True,
                "order": result
            }
        except Exception as e:
            logger.error(f"Failed to cancel order {order.id}: {e}", exc_info=True)
            raw_error = str(e)
            return {
                "success": False,
                "error": raw_error
            }
    
    def calculate_sl_tp_prices(
        self,
        entry_price: float,
        side: str,
        sl_percent: float,
        tp_percent: float
    ) -> Dict[str, float]:
        """Calculate stop loss and take profit prices"""
        if side.lower() == "buy":
            stop_loss = entry_price * (1 - sl_percent / 100)
            take_profit = entry_price * (1 + tp_percent / 100)
        else:  # sell
            stop_loss = entry_price * (1 + sl_percent / 100)
            take_profit = entry_price * (1 - tp_percent / 100)
        
        return {
            "stop_loss": stop_loss,
            "take_profit": take_profit
        }
    
    def calculate_trailing_stop(
        self,
        current_price: float,
        highest_price: float,
        trailing_percent: float,
        side: str
    ) -> float:
        """Calculate trailing stop price"""
        if side.lower() == "buy":
            # For long positions, trailing stop moves up
            trailing_stop = highest_price * (1 - trailing_percent / 100)
            return max(trailing_stop, current_price * (1 - trailing_percent / 100))
        else:  # sell
            # For short positions, trailing stop moves down
            trailing_stop = highest_price * (1 + trailing_percent / 100)
            return min(trailing_stop, current_price * (1 + trailing_percent / 100))
    
    def get_symbols(self, config: BotConfig) -> Dict:
        """Get list of available trading symbols from exchange"""
        try:
            exchange = self.get_exchange(config)
            markets = exchange.load_markets()
            
            # Filter symbols based on trading mode
            symbols = []
            for symbol, market in markets.items():
                # Filter by trading mode
                if config.trading_mode == 'spot':
                    if market.get('spot', False) and market.get('active', True):
                        symbols.append(symbol)
                elif config.trading_mode == 'futures':
                    if market.get('future', False) or market.get('swap', False):
                        if market.get('active', True):
                            symbols.append(symbol)
            
            # Sort symbols
            symbols.sort()
            
            return {
                "success": True,
                "symbols": symbols,
                "count": len(symbols)
            }
        except Exception as e:
            logger.error(f"Failed to get symbols: {e}")
            raw_error = str(e)
            return {
                "success": False,
                "error": raw_error,
                "symbols": []
            }
    
    def place_tp_sl_orders(
        self,
        config: BotConfig,
        symbol: str,
        side: str,
        amount: float,
        stop_loss_price: Optional[float],
        take_profit_price: Optional[float]
    ) -> Dict:
        """
        Đặt thêm lệnh TP/SL trên sàn (Binance Futures) cho position hiện tại.
        - Dùng lệnh reduceOnly, closePosition để đóng vị thế.
        - Chỉ hỗ trợ Binance Futures. Các trường hợp khác sẽ bỏ qua (no-op).
        """
        try:
            # Chỉ hỗ trợ Binance Futures
            if config.exchange.lower() != "binance" or config.trading_mode != "futures":
                return {
                    "success": True,
                    "message": "TP/SL placing skipped (only supported for Binance Futures)"
                }
            
            exchange = self.get_exchange(config)
            results: Dict[str, Optional[Dict]] = {
                "tp_order": None,
                "sl_order": None,
            }
            
            # Opposite side để đóng position
            opposite_side = "sell" if side.lower() == "buy" else "buy"
            
            # Đặt TP
            if take_profit_price:
                try:
                    params = {
                        "stopPrice": float(take_profit_price),
                        # Với Binance Futures: dùng closePosition, KHÔNG gửi reduceOnly
                        "closePosition": True,
                        "timeInForce": "GTC"
                    }
                    tp_order = exchange.create_order(
                        symbol,
                        "take_profit_market",
                        opposite_side,
                        amount,
                        None,
                        params
                    )
                    results["tp_order"] = tp_order
                    logger.info(f"Placed TP order on Binance: {tp_order}")
                except Exception as e:
                    error_msg = str(e)
                    if "4045" in error_msg or "max stop order limit" in error_msg.lower():
                        logger.warning(f"Failed to place TP order: Binance max stop order limit reached. Main order still successful.")
                    else:
                        logger.error(f"Failed to place TP order on Binance: {e}", exc_info=True)
                    results["tp_error"] = error_msg
            
            # Đặt SL
            if stop_loss_price:
                try:
                    params = {
                        "stopPrice": float(stop_loss_price),
                        # Với Binance Futures: dùng closePosition, KHÔNG gửi reduceOnly
                        "closePosition": True,
                        "timeInForce": "GTC"
                    }
                    sl_order = exchange.create_order(
                        symbol,
                        "stop_market",
                        opposite_side,
                        amount,
                        None,
                        params
                    )
                    results["sl_order"] = sl_order
                    logger.info(f"Placed SL order on Binance: {sl_order}")
                except Exception as e:
                    error_msg = str(e)
                    if "4045" in error_msg or "max stop order limit" in error_msg.lower():
                        logger.warning(f"Failed to place SL order: Binance max stop order limit reached. Main order still successful.")
                    else:
                        logger.error(f"Failed to place SL order on Binance: {e}", exc_info=True)
                    results["sl_error"] = error_msg
            
            return {
                "success": True,
                **results
            }
        except Exception as e:
            logger.error(f"Failed to place TP/SL orders: {e}", exc_info=True)
            raw_error = str(e)
            return {
                "success": False,
                "error": raw_error
            }
    
    def check_order_status(self, config: BotConfig, exchange_order_id: str) -> Dict:
        """Check order status on exchange"""
        try:
            exchange = self.get_exchange(config)
            order = exchange.fetch_order(exchange_order_id, config.symbol)
            return {
                "success": True,
                "order": order,
                "status": order.get("status"),
                "filled": order.get("filled", 0),
                "remaining": order.get("remaining", 0)
            }
        except Exception as e:
            logger.error(f"Failed to check order status: {e}")
            raw_error = str(e)
            return {
                "success": False,
                "error": raw_error
            }
    
    def close_position(self, config: BotConfig, order: Order) -> Dict:
        """
        Close a position and calculate PnL from exchange
        
        Returns:
            - success: bool
            - order: close order data
            - pnl: realized PnL (for futures) or calculated PnL (for spot)
            - pnl_percent: PnL percentage
            - close_price: price at which position was closed
        """
        try:
            exchange = self.get_exchange(config)
            symbol = order.symbol or config.symbol
            
            # Determine opposite side
            opposite_side = "sell" if order.side == "buy" else "buy"
            
            # Close with market order
            close_order = exchange.create_market_order(
                symbol,
                opposite_side,
                order.filled_amount
            )
            
            # Get close price
            close_price = close_order.get("price") or close_order.get("average") or close_order.get("last")
            
            # Calculate PnL based on trading mode
            pnl = 0.0
            pnl_percent = 0.0
            
            if config.trading_mode == "futures":
                # For futures, try to get PnL from position
                try:
                    positions = exchange.fetch_positions([symbol])
                    for pos in positions:
                        if pos.get("symbol") == symbol and pos.get("contracts", 0) != 0:
                            # Get realized PnL from position
                            realized_pnl = pos.get("info", {}).get("realizedProfit")
                            if realized_pnl is not None:
                                pnl = float(realized_pnl)
                            else:
                                # Calculate from entry/exit if not available
                                entry_price = pos.get("entryPrice") or order.filled_price
                                if entry_price and close_price:
                                    if order.side == "buy":
                                        pnl = (close_price - entry_price) * order.filled_amount * config.leverage
                                    else:
                                        pnl = (entry_price - close_price) * order.filled_amount * config.leverage
                            break
                except Exception as e:
                    logger.warning(f"Could not fetch position PnL: {e}, calculating manually")
                    # Fall through to manual calculation
            
            # For spot or if futures PnL not available, calculate manually
            if pnl == 0.0 and order.filled_price and close_price:
                entry_price = order.filled_price
                if order.side == "buy":
                    # Long position: profit = (exit - entry) * amount
                    pnl = (close_price - entry_price) * order.filled_amount
                else:
                    # Short position: profit = (entry - exit) * amount
                    pnl = (entry_price - close_price) * order.filled_amount
                
                # Calculate PnL percentage
                entry_cost = entry_price * order.filled_amount
                if entry_cost > 0:
                    pnl_percent = (pnl / entry_cost) * 100
            
            # For futures, calculate ROI based on margin (để gần với ROI của Binance)
            if config.trading_mode == "futures" and pnl != 0.0 and order.filled_price and config.leverage:
                notional = order.filled_price * order.filled_amount  # Giá trị vị thế
                margin = notional / config.leverage                 # Số tiền ký quỹ
                if margin > 0:
                    pnl_percent = (pnl / margin) * 100
            
            logger.info(f"Position closed: PnL={pnl}, PnL%={pnl_percent}, Close price={close_price}")
            
            return {
                "success": True,
                "order": close_order,
                "pnl": pnl,
                "pnl_percent": pnl_percent,
                "close_price": close_price
            }
        except Exception as e:
            logger.error(f"Failed to close position: {e}")
            raw_error = str(e)
            return {
                "success": False,
                "error": raw_error
            }


    def get_pnl_from_exchange(self, config: BotConfig, order: Order) -> Dict:
        """
        Lấy PnL từ sàn cho một order (không đóng lệnh)
        
        Returns:
            - success: bool
            - pnl: PnL từ sàn
            - pnl_percent: PnL percentage
            - current_price: Giá hiện tại (cho unrealized PnL)
        """
        try:
            exchange = self.get_exchange(config)
            symbol = order.symbol or config.symbol
            
            pnl = 0.0
            pnl_percent = 0.0
            current_price = None
            
            if config.trading_mode == "futures":
                # For futures, get PnL from position
                try:
                    positions = exchange.fetch_positions([symbol])
                    for pos in positions:
                        if pos.get("symbol") == symbol:
                            # Get unrealized PnL for open positions
                            unrealized_pnl = pos.get("unrealizedPnl")
                            if unrealized_pnl is not None:
                                pnl = float(unrealized_pnl)
                            else:
                                # Calculate from entry and current price
                                entry_price = pos.get("entryPrice") or order.filled_price
                                current_price = pos.get("markPrice") or pos.get("mark")
                                if entry_price and current_price:
                                    if order.side == "buy":
                                        pnl = (current_price - entry_price) * order.filled_amount * config.leverage
                                    else:
                                        pnl = (entry_price - current_price) * order.filled_amount * config.leverage
                            
                            # Get realized PnL if position is closed
                            if pos.get("contracts", 0) == 0 and order.status == "closed":
                                realized_pnl = pos.get("info", {}).get("realizedProfit")
                                if realized_pnl is not None:
                                    pnl = float(realized_pnl)
                            
                            if current_price is None:
                                current_price = pos.get("markPrice") or pos.get("mark")
                            break
                except Exception as e:
                    logger.warning(f"Could not fetch position PnL: {e}, calculating manually")
                    # Fall through to manual calculation
            
            # For spot or if futures PnL not available, calculate from current price
            if pnl == 0.0 or current_price is None:
                try:
                    ticker = exchange.fetch_ticker(symbol)
                    current_price = ticker.get("last") or ticker.get("close")
                except Exception as e:
                    logger.warning(f"Could not fetch ticker: {e}")
                    current_price = None
            
            # Calculate PnL manually if we have entry price and current price
            if order.filled_price and current_price:
                entry_price = order.filled_price
                
                if order.status == "closed":
                    # For closed orders, use close_price if available
                    if hasattr(order, 'closed_at') and order.closed_at:
                        # Already closed, PnL should be in DB
                        # But we can recalculate if needed
                        pass
                else:
                    # For open orders, calculate unrealized PnL
                    if order.side == "buy":
                        pnl = (current_price - entry_price) * order.filled_amount
                    else:
                        pnl = (entry_price - current_price) * order.filled_amount
                    
                    # Apply leverage for futures
                    if config.trading_mode == "futures":
                        pnl = pnl * config.leverage
                
                # Calculate PnL percentage
                notional = entry_price * order.filled_amount
                if config.trading_mode == "futures" and config.leverage:
                    # ROI theo Binance ≈ PnL / margin
                    margin = notional / config.leverage
                    if margin > 0:
                        pnl_percent = (pnl / margin) * 100
                else:
                    if notional > 0:
                        pnl_percent = (pnl / notional) * 100
            
            logger.info(f"PnL from exchange: PnL={pnl}, PnL%={pnl_percent}, Current price={current_price}")
            
            return {
                "success": True,
                "pnl": pnl,
                "pnl_percent": pnl_percent,
                "current_price": current_price
            }
        except Exception as e:
            logger.error(f"Failed to get PnL from exchange: {e}")
            raw_error = str(e)
            return {
                "success": False,
                "error": raw_error
            }

    def _binance_futures_signature(self, params: dict, secret: str) -> str:
        """Tạo signature cho Binance Futures API"""
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def fetch_pnl_by_order_id_binance_futures(
        self, 
        config: BotConfig, 
        order: Order
    ) -> Dict:
        """
        Lấy PnL/ROI từ Binance Futures API dựa trên exchange_order_id
        Tính theo đúng cách Binance tính (dựa trên trades và margin)
        """
        try:
            if not order.exchange_order_id:
                return {
                    "success": False,
                    "error": "Order không có exchange_order_id"
                }
            
            if config.trading_mode != "futures":
                return {
                    "success": False,
                    "error": "Chỉ hỗ trợ Futures trading"
                }
            
            # Get API credentials
            api_key = decrypt_data(config.api_key_encrypted)
            api_secret = decrypt_data(config.api_secret_encrypted)
            
            # Binance Futures API base URL
            base_url = "https://fapi.binance.com"
            
            # 1. Lấy tất cả trades của orderId này
            symbol = order.symbol.replace('/', '')  # BTC/USDT -> BTCUSDT
            
            params = {
                'symbol': symbol,
                'orderId': order.exchange_order_id,
                'timestamp': int(time.time() * 1000)
            }
            
            params['signature'] = self._binance_futures_signature(params, api_secret)
            
            headers = {
                'X-MBX-APIKEY': api_key
            }
            
            # GET /fapi/v1/userTrades
            response = requests.get(
                f"{base_url}/fapi/v1/userTrades",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                error_msg = response.json().get('msg', 'Unknown error')
                logger.error(f"Binance API error: {error_msg}")
                return {
                    "success": False,
                    "error": f"Binance API error: {error_msg}"
                }
            
            trades = response.json()
            
            if not trades:
                # Không có trades, có thể order chưa fill hoặc đã quá lâu
                return {
                    "success": False,
                    "error": "Không tìm thấy trades cho orderId này"
                }
            
            # 2. Tính PnL từ trades
            # Binance tính PnL = sum(realizedPnl từ mỗi trade)
            total_pnl = 0.0
            total_commission = 0.0
            total_quantity = 0.0
            entry_price_sum = 0.0
            
            for trade in trades:
                # realizedPnl từ Binance (đã tính sẵn)
                realized_pnl = float(trade.get('realizedPnl', 0))
                total_pnl += realized_pnl
                
                # Commission
                commission = float(trade.get('commission', 0))
                total_commission += commission
                
                # Quantity và price để tính entry cost
                qty = float(trade.get('qty', 0))
                price = float(trade.get('price', 0))
                total_quantity += qty
                entry_price_sum += price * qty
            
            # Net PnL (trừ commission)
            net_pnl = total_pnl - total_commission
            
            # 3. Tính ROI theo cách Binance
            # ROI = PnL / Margin * 100
            # Margin = Notional Value / Leverage
            # Notional Value = Entry Price * Quantity
            
            if total_quantity > 0:
                avg_entry_price = entry_price_sum / total_quantity
            else:
                avg_entry_price = order.filled_price or 0
            
            notional_value = avg_entry_price * total_quantity
            leverage = config.leverage or 1
            margin = notional_value / leverage if leverage > 0 else notional_value
            
            # Tính ROI
            if margin > 0:
                roi_percent = (net_pnl / margin) * 100
            else:
                roi_percent = 0.0
            
            logger.info(
                f"Binance PnL for order {order.exchange_order_id}: "
                f"PnL={net_pnl}, ROI={roi_percent}%, Margin={margin}, "
                f"Trades={len(trades)}"
            )
            
            return {
                "success": True,
                "pnl": net_pnl,
                "pnl_percent": roi_percent,
                "margin": margin,
                "trades_count": len(trades),
                "commission": total_commission
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch PnL from Binance Futures API: {e}", exc_info=True)
            raw_error = str(e)
            return {
                "success": False,
                "error": raw_error
            }

    def fetch_position_history(self, config: BotConfig, symbol: Optional[str] = None, limit: int = 100) -> Dict:
        """
        Fetch position history from Binance (closed positions)
        
        For Binance Futures, we can use:
        - fapi/v1/userTrades (trade history)
        - Or fetch_positions and filter closed ones
        
        Returns:
            - success: bool
            - positions: List of closed positions with PnL
        """
        try:
            exchange = self.get_exchange(config)
            
            if config.trading_mode != "futures":
                return {
                    "success": False,
                    "error": "Position history chỉ hỗ trợ Futures trading"
                }
            
            # For Binance, try to get position history
            # Note: CCXT may not support position history directly
            # We'll use fetch_my_trades to reconstruct position history
            positions_history = []
            
            try:
                # Get all trades for the symbol
                symbol_to_fetch = symbol or config.symbol
                trades = exchange.fetch_my_trades(symbol_to_fetch, limit=limit)
                
                # Group trades by position (entry + exit)
                # This is a simplified approach - in reality, Binance tracks positions internally
                # For accurate position history, we'd need to use Binance API directly
                
                # Try to use Binance-specific API if available
                if hasattr(exchange, 'fapiPrivateGetUserTrades'):
                    # Binance Futures API: GET /fapi/v1/userTrades
                    try:
                        params = {}
                        if symbol_to_fetch:
                            params['symbol'] = symbol_to_fetch
                        if limit:
                            params['limit'] = limit
                        
                        # Use private API call
                        response = exchange.fapiPrivateGetUserTrades(params)
                        
                        # Process trades to group into positions
                        # This requires matching entry/exit trades
                        logger.info(f"Fetched {len(response)} trades from Binance")
                        
                    except Exception as e:
                        logger.warning(f"Could not use Binance-specific API: {e}, using CCXT trades")
                        trades = exchange.fetch_my_trades(symbol_to_fetch, limit=limit)
                else:
                    trades = exchange.fetch_my_trades(symbol_to_fetch, limit=limit)
                
                # For now, return trades as position history
                # In a full implementation, we'd need to:
                # 1. Match entry/exit trades
                # 2. Calculate realized PnL per position
                # 3. Group by position ID
                
                positions_history = trades[:limit]
                
            except Exception as e:
                logger.error(f"Failed to fetch position history: {e}", exc_info=True)
                raw_error = str(e)
                return {
                    "success": False,
                    "error": f"Không thể lấy lịch sử vị thế: {raw_error}"
                }
            
            return {
                "success": True,
                "positions": positions_history,
                "count": len(positions_history)
            }
            
        except Exception as e:
            logger.error(f"Error fetching position history: {e}", exc_info=True)
            raw_error = str(e)
            return {
                "success": False,
                "error": raw_error
            }


trading_service = TradingService()


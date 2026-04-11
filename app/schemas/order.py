from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class OrderCreate(BaseModel):
    bot_config_id: int
    symbol: str
    side: str  # "buy" or "sell"
    order_type: str = "market"
    amount: float
    price: Optional[float] = None


class OrderResponse(BaseModel):
    id: int
    bot_config_id: int
    bot_config_name: Optional[str] = None  # Tên Bot Config để dễ tra cứu
    exchange_order_id: Optional[str]
    symbol: str
    side: str
    order_type: Optional[str] = "market"
    amount: float
    price: Optional[float] = None
    leverage: Optional[int] = 1
    status: str
    filled_amount: Optional[float] = 0.0
    filled_price: Optional[float]
    stop_loss_price: Optional[float]
    take_profit_price: Optional[float]
    tp_levels: Optional[List[Dict]] = []
    trailing_enabled: bool
    trailing_high_price: Optional[float]
    trailing_stop_price: Optional[float]
    pnl: float
    pnl_percent: float
    exchange: str
    trading_mode: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    closed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class OrderHistoryFilter(BaseModel):
    bot_config_id: Optional[int] = None
    symbol: Optional[str] = None
    status: Optional[str] = None
    side: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


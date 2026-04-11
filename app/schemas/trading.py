from pydantic import BaseModel, Field
from typing import Optional


class PlaceOrderRequest(BaseModel):
    """Request model for placing order directly"""
    bot_config_id: int = Field(..., description="Bot config ID")
    side: str = Field(..., pattern="^(buy|sell)$", description="Order side: buy or sell")
    symbol: Optional[str] = Field(None, description="Symbol to trade (uses config symbol if not provided)")
    amount: Optional[float] = Field(None, ge=0, description="Order amount (uses config amount if not provided or 0)")
    price: Optional[float] = Field(None, gt=0, description="Price for limit order (optional for market order)")
    order_type: str = Field("market", pattern="^(market|limit)$", description="Order type: market or limit")


class PlaceOrderResponse(BaseModel):
    """Response model for placed order"""
    status: str
    order_id: int
    exchange_order_id: Optional[str]
    symbol: str
    side: str
    order_type: str
    amount: float
    price: Optional[float]
    filled_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    order_status: str


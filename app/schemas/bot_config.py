from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class TPLevel(BaseModel):
    percent: float = Field(..., description="Take profit percentage")
    close_percent: float = Field(..., description="Percentage of position to close at this TP")


class BotConfigCreate(BaseModel):
    name: str
    symbol: str
    exchange: str = "binance"
    amount: float = Field(..., gt=0, description="Order amount")
    leverage: int = Field(default=1, ge=1, le=125, description="Leverage for futures")
    stop_loss_percent: float = Field(..., description="Stop loss percentage")
    take_profit_percent: float = Field(..., description="Take profit percentage")
    tp_levels: Optional[List[TPLevel]] = Field(default=[], description="Multiple TP levels")
    enable_trailing: bool = False
    trailing_type: str = Field(default="percent", pattern="^(percent|atr)$")
    trailing_percent: Optional[float] = Field(None, description="Trailing percentage")
    trailing_atr_multiplier: Optional[float] = Field(None, description="ATR multiplier for trailing")
    trailing_atr_period: int = Field(default=14, ge=1, le=100)
    api_key: Optional[str] = Field(None, description="Exchange API key (will be encrypted)")
    api_secret: Optional[str] = Field(None, description="Exchange API secret (will be encrypted)")
    ip_whitelist: Optional[str] = Field(None, description="IP whitelist for exchange API (comma-separated, e.g., '1.2.3.4,5.6.7.8')")
    trading_mode: str = Field(default="spot", pattern="^(spot|futures)$")
    max_open_positions: int = Field(default=1, ge=1)
    enable_notifications: bool = True


class BotConfigUpdate(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    leverage: Optional[int] = Field(None, ge=1, le=125)
    stop_loss_percent: Optional[float] = None
    take_profit_percent: Optional[float] = None
    tp_levels: Optional[List[TPLevel]] = None
    enable_trailing: Optional[bool] = None
    trailing_type: Optional[str] = Field(None, pattern="^(percent|atr)$")
    trailing_percent: Optional[float] = None
    trailing_atr_multiplier: Optional[float] = None
    trailing_atr_period: Optional[int] = Field(None, ge=1, le=100)
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    ip_whitelist: Optional[str] = None
    trading_mode: Optional[str] = Field(None, pattern="^(spot|futures)$")
    max_open_positions: Optional[int] = Field(None, ge=1)
    enable_notifications: Optional[bool] = None
    is_active: Optional[bool] = None


class BotConfigResponse(BaseModel):
    id: int
    name: str
    symbol: str
    exchange: str
    amount: float
    leverage: int
    stop_loss_percent: float
    take_profit_percent: float
    tp_levels: List[Dict]
    enable_trailing: bool
    trailing_type: str
    trailing_percent: Optional[float]
    trailing_atr_multiplier: Optional[float]
    trailing_atr_period: int
    trading_mode: str
    ip_whitelist: Optional[str]
    max_open_positions: int
    enable_notifications: bool
    is_active: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


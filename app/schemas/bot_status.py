from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class BotStatusSimple(BaseModel):
    """Basic bot status response"""
    bot_config_id: int
    status: str = Field(..., description="Status: Running, Paused, Stopped, Error, Idle, Completed")
    is_running: bool
    is_paused: bool
    total_orders: int
    successful_orders: int
    failed_orders: int
    total_pnl: float
    health_status: str
    last_error: Optional[str]
    last_error_time: Optional[datetime]
    last_heartbeat: Optional[datetime]
    updated_at: Optional[datetime]
    last_updated: Optional[datetime]
    
    class Config:
        from_attributes = True


class BotStatusResponse(BaseModel):
    """Comprehensive bot status with config details"""
    # BotStatus fields
    bot_config_id: int
    status: str = Field(..., description="Status: Running, Paused, Stopped, Error, Idle, Completed")
    is_running: bool
    is_paused: bool
    total_orders: int
    successful_orders: int
    failed_orders: int
    total_pnl: float
    health_status: str = Field(..., description="Health: healthy, warning, error, offline, unknown")
    last_error: Optional[str]
    last_error_time: Optional[datetime]
    last_heartbeat: Optional[datetime]
    consecutive_errors: int
    current_positions: Optional[List[Dict]]
    updated_at: Optional[datetime]
    last_updated: Optional[datetime]
    
    # BotConfig fields
    bot_name: str = Field(..., description="Bot name from BotConfig")
    symbol: str = Field(..., description="Trading symbol")
    exchange: str = Field(..., description="Exchange name")
    trading_mode: str = Field(..., description="Trading mode: spot or futures")
    is_active: bool = Field(..., description="Is bot active")
    amount: float = Field(..., description="Order amount")
    leverage: int = Field(..., description="Leverage for futures")
    
    # Display fields
    display_name: str = Field(..., description="Formatted display name: 'BTC_bot (ID: 1) - BTC/USDT - Binance'")
    
    class Config:
        from_attributes = True

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class BotConfig(Base):
    __tablename__ = "bot_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    exchange = Column(String(50), default="binance")
    
    # Trading parameters
    amount = Column(Float, nullable=False)  # Order amount
    leverage = Column(Integer, default=1)  # Leverage for futures
    
    # Stop Loss & Take Profit
    stop_loss_percent = Column(Float, nullable=False)  # SL in percentage
    take_profit_percent = Column(Float, nullable=False)  # TP in percentage
    
    # Multiple Take Profit levels
    tp_levels = Column(JSON, default=[])  # [{"percent": 1.0, "close_percent": 50}, ...]
    
    # Trailing Stop
    enable_trailing = Column(Boolean, default=False)
    trailing_type = Column(String(20), default="percent")  # "percent" or "atr"
    trailing_percent = Column(Float, nullable=True)  # Trailing percentage
    trailing_atr_multiplier = Column(Float, nullable=True)  # ATR multiplier
    trailing_atr_period = Column(Integer, default=14)  # ATR period
    
    # Exchange API credentials (encrypted)
    api_key_encrypted = Column(Text, nullable=True)
    api_secret_encrypted = Column(Text, nullable=True)
    ip_whitelist = Column(Text, nullable=True)  # IP whitelist for exchange API (comma-separated)
    
    # Trading mode
    trading_mode = Column(String(20), default="spot")  # "spot" or "futures"
    
    # Additional settings
    max_open_positions = Column(Integer, default=1)
    enable_notifications = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, nullable=True)  # User ID
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<BotConfig(id={self.id}, name={self.name}, symbol={self.symbol})>"


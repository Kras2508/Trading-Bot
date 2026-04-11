from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_config_id = Column(Integer, ForeignKey("bot_configs.id"), nullable=False, index=True)
    
    # Order details
    exchange_order_id = Column(String(100), unique=True, index=True, nullable=True)
    symbol = Column(String(50), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # "buy" or "sell"
    order_type = Column(String(20), default="market")  # "market", "limit", etc.
    
    # Trading parameters
    amount = Column(Float, nullable=False)
    price = Column(Float, nullable=True)  # Entry price
    leverage = Column(Integer, default=1)
    
    # Status
    status = Column(String(20), default="pending")  # pending, filled, cancelled, error, closed
    filled_amount = Column(Float, default=0.0)
    filled_price = Column(Float, nullable=True)
    
    # SL/TP
    stop_loss_price = Column(Float, nullable=True)
    take_profit_price = Column(Float, nullable=True)
    tp_levels = Column(JSON, default=[])  # Multiple TP levels
    
    # Trailing stop
    trailing_enabled = Column(Boolean, default=False)
    trailing_high_price = Column(Float, nullable=True)  # Highest price reached
    trailing_stop_price = Column(Float, nullable=True)  # Current trailing stop price
    
    # PnL
    pnl = Column(Float, default=0.0)
    pnl_percent = Column(Float, default=0.0)
    
    # Additional info
    exchange = Column(String(50), default="binance")
    trading_mode = Column(String(20), default="spot")
    raw_data = Column(JSON, nullable=True)  # Raw exchange response
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    bot_config = relationship("BotConfig", backref="orders")
    
    def __repr__(self):
        return f"<Order(id={self.id}, symbol={self.symbol}, side={self.side}, status={self.status})>"


from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text, Float
from sqlalchemy.sql import func
from app.database import Base


class BotStatus(Base):
    __tablename__ = "bot_status"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_config_id = Column(Integer, unique=True, nullable=False, index=True)
    
    # Status
    status = Column(String(20), default="Idle")  # Running, Paused, Stopped, Error, Idle, Completed
    is_running = Column(Boolean, default=False)
    is_paused = Column(Boolean, default=False)
    last_activity = Column(DateTime(timezone=True), nullable=True)
    
    # Statistics
    total_orders = Column(Integer, default=0)
    successful_orders = Column(Integer, default=0)
    failed_orders = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)
    
    # Current state
    current_positions = Column(JSON, default=[])  # List of open positions
    last_error = Column(Text, nullable=True)
    last_error_time = Column(DateTime(timezone=True), nullable=True)
    consecutive_errors = Column(Integer, default=0)  # For health calculation
    
    # Health check
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    health_status = Column(String(20), default="unknown")  # healthy, warning, error, offline, unknown
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_updated = Column(DateTime(timezone=True), nullable=True)  # Status last updated
    
    def __repr__(self):
        return f"<BotStatus(bot_config_id={self.bot_config_id}, status={self.status})>"


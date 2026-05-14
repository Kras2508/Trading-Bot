from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.bot_status import BotStatus


class HealthCheckService:
    """Service for calculating and updating bot health status"""
    
    # Configuration
    HEARTBEAT_TIMEOUT_MINUTES = 5  # If no heartbeat for 5 minutes, mark offline
    ERROR_WARNING_THRESHOLD = 3  # If 3+ consecutive errors, mark warning
    ERROR_CRITICAL_THRESHOLD = 5  # If 5+ consecutive errors, mark error
    
    @staticmethod
    def calculate_health(bot_status: BotStatus) -> str:
        """
        Calculate health status based on:
        - last_heartbeat: If no heartbeat for > 5 min, mark offline
        - consecutive_errors: If 5+ errors, mark error; if 3+, mark warning
        - status: If paused, still healthy (paused is not an error)
        - is_running: If not running, could be idle/stopped
        
        Returns: 'healthy', 'warning', 'error', 'offline', 'unknown'
        """
        
        # If paused, still healthy (user intentionally paused)
        if bot_status.is_paused:
            return "healthy"
        
        now = datetime.utcnow()
        heartbeat_timeout = now - timedelta(minutes=HealthCheckService.HEARTBEAT_TIMEOUT_MINUTES)
        
        # If bot is running and no heartbeat for 5+ minutes, mark offline
        if bot_status.is_running:
            if bot_status.last_heartbeat is None or bot_status.last_heartbeat < heartbeat_timeout:
                return "offline"
        
        # Check consecutive errors
        if bot_status.consecutive_errors >= HealthCheckService.ERROR_CRITICAL_THRESHOLD:
            return "error"
        
        if bot_status.consecutive_errors >= HealthCheckService.ERROR_WARNING_THRESHOLD:
            return "warning"
        
        # Check if there's a recent error
        if bot_status.last_error and bot_status.last_error_time:
            error_timeout = now - timedelta(minutes=10)
            if bot_status.last_error_time > error_timeout:
                return "warning"
        
        # If not running and not paused, it might be idle
        if not bot_status.is_running and not bot_status.is_paused:
            return "healthy"  # Could be idle or stopped, still healthy
        
        # Default: healthy
        return "healthy"
    
    @staticmethod
    def update_health_status(bot_status: BotStatus, db: Session = None) -> str:
        """Calculate and update bot health status in database"""
        new_health = HealthCheckService.calculate_health(bot_status)
        
        if bot_status.health_status != new_health:
            bot_status.health_status = new_health
            bot_status.updated_at = datetime.utcnow()
            
            if db:
                db.commit()
        
        return new_health
    
    @staticmethod
    def record_error(bot_status: BotStatus, error_message: str, db: Session) -> None:
        """Record an error and update consecutive error count"""
        bot_status.last_error = error_message
        bot_status.last_error_time = datetime.utcnow()
        bot_status.consecutive_errors += 1
        bot_status.updated_at = datetime.utcnow()
        
        # Update health based on new error count
        HealthCheckService.update_health_status(bot_status, db)
        db.commit()
    
    @staticmethod
    def clear_errors(bot_status: BotStatus, db: Session) -> None:
        """Clear error state (on successful operation)"""
        bot_status.consecutive_errors = 0
        bot_status.updated_at = datetime.utcnow()
        
        # Update health status
        HealthCheckService.update_health_status(bot_status, db)
        db.commit()
    
    @staticmethod
    def record_heartbeat(bot_status: BotStatus, db: Session) -> None:
        """Record heartbeat from bot"""
        bot_status.last_heartbeat = datetime.utcnow()
        bot_status.updated_at = datetime.utcnow()
        
        # Update health based on heartbeat
        HealthCheckService.update_health_status(bot_status, db)
        db.commit()

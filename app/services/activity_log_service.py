import logging
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.models.activity_log import ActivityLog
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class ActivityLogService:
    """Service for logging activities"""
    
    def log_activity(
        self,
        db: Session,
        level: str,
        category: str,
        message: str,
        bot_config_id: Optional[int] = None,
        order_id: Optional[int] = None,
        details: Optional[Dict] = None,
        source_ip: Optional[str] = None
    ):
        """Log an activity"""
        try:
            # Normalize details to JSON-compatible types using jsonable_encoder
            if details is not None:
                try:
                    details = jsonable_encoder(details)
                except Exception as enc_err:
                    logger.warning(f"Failed to encode activity log details: {enc_err}")
                    details = {"serialization_error": str(enc_err), "raw_details": str(details)}

            log_entry = ActivityLog(
                bot_config_id=bot_config_id,
                order_id=order_id,
                level=level,
                category=category,
                message=message,
                details=details,
                source_ip=source_ip
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
            db.rollback()


activity_log_service = ActivityLogService()

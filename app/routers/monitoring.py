from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.bot_status import BotStatus
from app.models.activity_log import ActivityLog
from app.schemas.activity_log import ActivityLogResponse
from app.core.security import verify_token
from app.services.telegram_service import telegram_service

router = APIRouter()


@router.get("/status")
async def get_all_bot_status(
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get status of all bots"""
    statuses = db.query(BotStatus).all()
    return statuses


@router.get("/status/{bot_config_id}")
async def get_bot_status(
    bot_config_id: int,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get status of a specific bot"""
    bot_status = db.query(BotStatus).filter(
        BotStatus.bot_config_id == bot_config_id
    ).first()
    
    if not bot_status:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=404, detail="Bot status not found")
    
    return bot_status


@router.post("/status/{bot_config_id}/pause")
async def pause_bot(
    bot_config_id: int,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Pause a bot"""
    bot_status = db.query(BotStatus).filter(
        BotStatus.bot_config_id == bot_config_id
    ).first()
    
    if not bot_status:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=404, detail="Bot status not found")
    
    bot_status.is_paused = True
    bot_status.is_running = False
    db.commit()
    
    # Send Telegram notification
    from app.models.bot_config import BotConfig
    config = db.query(BotConfig).filter(BotConfig.id == bot_config_id).first()
    if config and config.enable_notifications:
        telegram_service.send_bot_paused_alert(config.name, "Manually paused")
    
    return {"status": "paused", "bot_config_id": bot_config_id}


@router.post("/status/{bot_config_id}/resume")
async def resume_bot(
    bot_config_id: int,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Resume a bot"""
    bot_status = db.query(BotStatus).filter(
        BotStatus.bot_config_id == bot_config_id
    ).first()
    
    if not bot_status:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=404, detail="Bot status not found")
    
    bot_status.is_paused = False
    bot_status.is_running = True
    db.commit()
    
    # Send Telegram notification
    from app.models.bot_config import BotConfig
    config = db.query(BotConfig).filter(BotConfig.id == bot_config_id).first()
    if config and config.enable_notifications:
        telegram_service.send_bot_status(config.name, "Resumed", "Bot has been resumed")
    
    return {"status": "resumed", "bot_config_id": bot_config_id}


@router.get("/logs", response_model=List[ActivityLogResponse])
async def get_activity_logs(
    bot_config_id: int = None,
    level: str = None,
    category: str = None,
    limit: int = 100,
    offset: int = 0,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get activity logs with filtering"""
    query = db.query(ActivityLog)
    
    if bot_config_id:
        query = query.filter(ActivityLog.bot_config_id == bot_config_id)
    
    if level:
        query = query.filter(ActivityLog.level == level)
    
    if category:
        query = query.filter(ActivityLog.category == category)
    
    # Order once to avoid duplicate ORDER BY in SQL Server
    query = query.order_by(ActivityLog.created_at.desc())
    logs = query.offset(offset).limit(limit).all()
    
    return logs


@router.get("/health")
async def health_check(
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """System health check"""
    # Check for bots that haven't sent heartbeat in 5 minutes
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    
    unhealthy_bots = db.query(BotStatus).filter(
        BotStatus.is_running == True,
        or_(
            BotStatus.last_heartbeat < five_minutes_ago,
            BotStatus.last_heartbeat == None
        )
    ).all()
    
    return {
        "status": "healthy" if not unhealthy_bots else "warning",
        "unhealthy_bots": len(unhealthy_bots),
        "timestamp": datetime.utcnow()
    }


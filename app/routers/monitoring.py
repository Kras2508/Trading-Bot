from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from sqlalchemy import or_

from app.database import get_db
from app.models.bot_status import BotStatus
from app.models.bot_config import BotConfig
from app.models.activity_log import ActivityLog
from app.schemas.activity_log import ActivityLogResponse
from app.schemas.bot_status import BotStatusResponse
from app.core.security import verify_token
from app.services.telegram_service import telegram_service
from app.services.health_check_service import HealthCheckService

router = APIRouter()


def format_bot_status(bot_status: BotStatus, bot_config: BotConfig) -> BotStatusResponse:
    """Convert BotStatus + BotConfig to BotStatusResponse"""
    display_name = f"{bot_config.name} (ID: {bot_config.id}) - {bot_config.symbol} - {bot_config.exchange.capitalize()}"
    
    return BotStatusResponse(
        # BotStatus fields
        bot_config_id=bot_status.bot_config_id,
        status=bot_status.status,
        is_running=bot_status.is_running,
        is_paused=bot_status.is_paused,
        total_orders=bot_status.total_orders,
        successful_orders=bot_status.successful_orders,
        failed_orders=bot_status.failed_orders,
        total_pnl=bot_status.total_pnl,
        health_status=bot_status.health_status,
        last_error=bot_status.last_error,
        last_error_time=bot_status.last_error_time,
        last_heartbeat=bot_status.last_heartbeat,
        consecutive_errors=bot_status.consecutive_errors,
        current_positions=bot_status.current_positions,
        updated_at=bot_status.updated_at,
        last_updated=bot_status.last_updated,
        
        # BotConfig fields
        bot_name=bot_config.name,
        symbol=bot_config.symbol,
        exchange=bot_config.exchange,
        trading_mode=bot_config.trading_mode,
        is_active=bot_config.is_active,
        amount=bot_config.amount,
        leverage=bot_config.leverage,
        
        # Display name
        display_name=display_name
    )


@router.get("/status", response_model=List[BotStatusResponse])
async def get_all_bot_status(
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get status of all active bots with bot config details"""
    # Get all BotStatus with their BotConfig
    # Use outerjoin to include all BotStatus, then filter later
    from sqlalchemy.orm import joinedload
    
    statuses = db.query(BotStatus).all()
    
    result = []
    for bot_status in statuses:
        bot_config = db.query(BotConfig).filter(
            BotConfig.id == bot_status.bot_config_id
        ).first()
        
        # Only include if bot_config exists and is active
        if bot_config and bot_config.is_active:
            result.append(format_bot_status(bot_status, bot_config))
    
    return result


@router.get("/status/{bot_config_id}", response_model=BotStatusResponse)
async def get_bot_status(
    bot_config_id: int,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get status of a specific bot with bot config details"""
    bot_status = db.query(BotStatus).filter(
        BotStatus.bot_config_id == bot_config_id
    ).first()
    
    if not bot_status:
        raise HTTPException(status_code=404, detail="Bot status not found")
    
    bot_config = db.query(BotConfig).filter(
        BotConfig.id == bot_config_id
    ).first()
    
    if not bot_config:
        raise HTTPException(status_code=404, detail="Bot config not found")
    
    return format_bot_status(bot_status, bot_config)


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
        raise HTTPException(status_code=404, detail="Bot status not found")
    
    bot_config = db.query(BotConfig).filter(
        BotConfig.id == bot_config_id
    ).first()
    
    if not bot_config:
        raise HTTPException(status_code=404, detail="Bot config not found")
    
    bot_status.is_paused = True
    bot_status.is_running = False
    bot_status.status = "Paused"
    bot_status.updated_at = datetime.utcnow()
    bot_status.last_updated = datetime.utcnow()
    db.commit()
    
    # Send Telegram notification
    if bot_config.enable_notifications:
        telegram_service.send_bot_paused_alert(bot_config.name, "Manually paused")
    
    return {"status": "Paused", "bot_config_id": bot_config_id}


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
        raise HTTPException(status_code=404, detail="Bot status not found")
    
    bot_config = db.query(BotConfig).filter(
        BotConfig.id == bot_config_id
    ).first()
    
    if not bot_config:
        raise HTTPException(status_code=404, detail="Bot config not found")
    
    if not bot_config.is_active:
        raise HTTPException(status_code=400, detail="Cannot resume inactive bot")
    
    bot_status.is_paused = False
    bot_status.is_running = True
    bot_status.status = "Running"
    bot_status.updated_at = datetime.utcnow()
    bot_status.last_updated = datetime.utcnow()
    db.commit()
    
    # Send Telegram notification
    if bot_config.enable_notifications:
        telegram_service.send_bot_status(bot_config.name, "Resumed", "Bot has been resumed")
    
    return {"status": "Running", "bot_config_id": bot_config_id}


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
    """System health check - updates health status for all bots"""
    # Update health status for all bots
    all_bots = db.query(BotStatus).all()
    
    unhealthy_bots = []
    for bot_status in all_bots:
        new_health = HealthCheckService.calculate_health(bot_status)
        if bot_status.health_status != new_health:
            bot_status.health_status = new_health
            bot_status.updated_at = datetime.utcnow()
        
        if new_health != "healthy":
            unhealthy_bots.append({
                "bot_config_id": bot_status.bot_config_id,
                "health": new_health
            })
    
    db.commit()
    
    return {
        "status": "healthy" if not unhealthy_bots else "warning",
        "unhealthy_bots": unhealthy_bots,
        "total_bots": len(all_bots),
        "timestamp": datetime.utcnow()
    }


@router.post("/health/refresh")
async def refresh_health(
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Manually refresh health status for all bots"""
    all_bots = db.query(BotStatus).all()
    
    refreshed_count = 0
    for bot_status in all_bots:
        old_health = bot_status.health_status
        new_health = HealthCheckService.calculate_health(bot_status)
        
        if old_health != new_health:
            bot_status.health_status = new_health
            bot_status.updated_at = datetime.utcnow()
            refreshed_count += 1
    
    db.commit()
    
    return {
        "refreshed": refreshed_count,
        "total": len(all_bots),
        "timestamp": datetime.utcnow()
    }


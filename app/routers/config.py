from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.bot_config import BotConfig
from app.schemas.bot_config import BotConfigCreate, BotConfigUpdate, BotConfigResponse
from app.core.security import verify_token, encrypt_data
from app.services.activity_log_service import activity_log_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=BotConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_config(
    config_data: BotConfigCreate,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create a new bot configuration"""
    # Get user ID
    from app.models.user import User
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Encrypt API credentials if provided
    api_key_encrypted = None
    api_secret_encrypted = None
    if config_data.api_key and config_data.api_secret:
        try:
            api_key_encrypted = encrypt_data(config_data.api_key)
            api_secret_encrypted = encrypt_data(config_data.api_secret)
        except Exception as e:
            logger.error(f"Failed to encrypt API credentials: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to encrypt API credentials"
            )
    
    # Create config
    db_config = BotConfig(
        name=config_data.name,
        symbol=config_data.symbol,
        exchange=config_data.exchange,
        amount=config_data.amount,
        leverage=config_data.leverage,
        stop_loss_percent=config_data.stop_loss_percent,
        take_profit_percent=config_data.take_profit_percent,
        tp_levels=[tp.dict() for tp in (config_data.tp_levels or [])],
        enable_trailing=config_data.enable_trailing,
        trailing_type=config_data.trailing_type,
        trailing_percent=config_data.trailing_percent,
        trailing_atr_multiplier=config_data.trailing_atr_multiplier,
        trailing_atr_period=config_data.trailing_atr_period,
        api_key_encrypted=api_key_encrypted,
        api_secret_encrypted=api_secret_encrypted,
        ip_whitelist=config_data.ip_whitelist,
        trading_mode=config_data.trading_mode,
        max_open_positions=config_data.max_open_positions,
        enable_notifications=config_data.enable_notifications,
        created_by=user.id
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    # Log activity
    activity_log_service.log_activity(
        db=db,
        level="info",
        category="config",
        message=f"Bot config created: {config_data.name}",
        bot_config_id=db_config.id
    )
    
    # Initialize bot status
    from app.models.bot_status import BotStatus
    bot_status = BotStatus(bot_config_id=db_config.id)
    db.add(bot_status)
    db.commit()
    
    logger.info(f"Bot config created: {db_config.id} - {db_config.name}")
    return db_config


@router.get("/", response_model=List[BotConfigResponse])
async def list_configs(
    skip: int = 0,
    limit: int = 100,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """List all bot configurations"""
    try:
        # SQL Server requires ORDER BY when using OFFSET/LIMIT
        configs = db.query(BotConfig).order_by(BotConfig.id).offset(skip).limit(limit).all()
        logger.info(f"Found {len(configs)} configs for user {username}")
        return configs
    except Exception as e:
        logger.error(f"Error listing configs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch configs: {str(e)}"
        )


@router.get("/{config_id}", response_model=BotConfigResponse)
async def get_config(
    config_id: int,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get a specific bot configuration"""
    config = db.query(BotConfig).filter(BotConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


@router.put("/{config_id}", response_model=BotConfigResponse)
async def update_config(
    config_id: int,
    config_data: BotConfigUpdate,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Update a bot configuration"""
    config = db.query(BotConfig).filter(BotConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Update fields
    update_data = config_data.dict(exclude_unset=True)
    
    # Handle API credentials encryption
    if "api_key" in update_data and update_data["api_key"]:
        update_data["api_key_encrypted"] = encrypt_data(update_data.pop("api_key"))
    if "api_secret" in update_data and update_data["api_secret"]:
        update_data["api_secret_encrypted"] = encrypt_data(update_data.pop("api_secret"))
    
    # Handle TP levels
    if "tp_levels" in update_data and update_data["tp_levels"] is not None:
        update_data["tp_levels"] = [tp.dict() if hasattr(tp, 'dict') else tp for tp in update_data["tp_levels"]]
    
    for field, value in update_data.items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    
    # Log activity
    activity_log_service.log_activity(
        db=db,
        level="info",
        category="config",
        message=f"Bot config updated: {config.name}",
        bot_config_id=config.id
    )
    
    logger.info(f"Bot config updated: {config.id} - {config.name}")
    return config


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(
    config_id: int,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Delete a bot configuration"""
    from app.models.order import Order
    
    config = db.query(BotConfig).filter(BotConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Check if there are orders associated with this config
    orders_count = db.query(Order).filter(Order.bot_config_id == config_id).count()
    
    if orders_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete bot config: {orders_count} order(s) are associated with this config. Please delete or reassign orders first."
        )
    
    # Log activity
    activity_log_service.log_activity(
        db=db,
        level="info",
        category="config",
        message=f"Bot config deleted: {config.name}",
        bot_config_id=config.id
    )
    
    db.delete(config)
    db.commit()
    
    logger.info(f"Bot config deleted: {config.id} - {config.name}")
    return None


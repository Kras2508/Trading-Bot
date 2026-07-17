from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.bot_config import BotConfig
from app.models.bot_status import BotStatus
from app.schemas.bot_config import BotConfigCreate, BotConfigUpdate, BotConfigResponse
from app.core.security import verify_token, encrypt_data
from app.services.activity_log_service import activity_log_service
from app.services.bot_config_service import validate_create_payload, validate_update_payload
from app.exceptions.error_code import ErrorCode
from app.exceptions.error_exception import ErrorException
from app.exceptions.logical_exception import NotFoundException
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
        raise NotFoundException(message="User not found")

    validated_data = validate_create_payload(config_data.model_dump())
    
    # Encrypt API credentials if provided
    api_key_encrypted = None
    api_secret_encrypted = None
    if config_data.api_key and config_data.api_secret:
        try:
            api_key_encrypted = encrypt_data(config_data.api_key)
            api_secret_encrypted = encrypt_data(config_data.api_secret)
        except Exception as e:
            logger.error(f"Failed to encrypt API credentials: {e}")
            raise ErrorException(
                error_code=ErrorCode.UNDEFINED_ERROR,
                message="Failed to encrypt API credentials"
            )
    
    # Create config
    db_config = BotConfig(
        name=validated_data["name"],
        symbol=validated_data["symbol"],
        exchange=validated_data["exchange"],
        amount=validated_data["amount"],
        leverage=validated_data["leverage"],
        stop_loss_percent=validated_data["stop_loss_percent"],
        take_profit_percent=validated_data["take_profit_percent"],
        tp_levels=validated_data.get("tp_levels", []),
        enable_trailing=validated_data["enable_trailing"],
        trailing_type=validated_data["trailing_type"],
        trailing_percent=validated_data.get("trailing_percent"),
        trailing_atr_multiplier=validated_data.get("trailing_atr_multiplier"),
        trailing_atr_period=validated_data["trailing_atr_period"],
        api_key_encrypted=api_key_encrypted,
        api_secret_encrypted=api_secret_encrypted,
        ip_whitelist=validated_data.get("ip_whitelist"),
        trading_mode=validated_data["trading_mode"],
        max_open_positions=validated_data["max_open_positions"],
        enable_notifications=validated_data["enable_notifications"],
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
    active_only: bool = False,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """List all bot configurations"""
    try:
        query = db.query(BotConfig)
        
        # Optional filter: only active bots
        if active_only:
            query = query.filter(BotConfig.is_active == True)
        
        # SQL Server requires ORDER BY when using OFFSET/LIMIT
        configs = db.query(BotConfig).order_by(BotConfig.id).offset(skip).limit(limit).all()
        config_ids = [config.id for config in configs]

        if config_ids:
            statuses = db.query(BotStatus).filter(BotStatus.bot_config_id.in_(config_ids)).all()
            status_map = {s.bot_config_id: s for s in statuses}

            for config in configs:
                bot_status_item = status_map.get(config.id)
                config.is_paused = bot_status_item.is_paused if bot_status_item else False

        logger.info(f"Found {len(configs)} configs for user {username}")
        return configs
    except (HTTPException, ErrorException):
        raise
    except Exception as e:
        logger.error(f"Error listing configs: {e}", exc_info=True)
        raise ErrorException(
            error_code=ErrorCode.UNDEFINED_ERROR,
            message=f"Failed to fetch configs: {str(e)}"
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
        raise NotFoundException(message="Configuration not found")

    status = db.query(BotStatus).filter(BotStatus.bot_config_id == config_id).first()
    config.is_paused = status.is_paused if status else False
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
        raise NotFoundException(message="Configuration not found")
    
    # Update fields
    update_data = config_data.dict(exclude_unset=True)
    
    update_data = validate_update_payload(update_data, config)

    # Handle API credentials encryption
    if "api_key" in update_data and not update_data["api_key"]:
        update_data.pop("api_key")
    if "api_secret" in update_data and not update_data["api_secret"]:
        update_data.pop("api_secret")

    if "api_key" in update_data:
        update_data["api_key_encrypted"] = encrypt_data(update_data.pop("api_key"))
    if "api_secret" in update_data:
        update_data["api_secret_encrypted"] = encrypt_data(update_data.pop("api_secret"))

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
    """Delete a bot configuration and cleanup dependent data."""
    from app.models.order import Order
    from app.models.bot_status import BotStatus
    
    config = db.query(BotConfig).filter(BotConfig.id == config_id).first()
    if not config:
        raise NotFoundException(message="Configuration not found")
    
    # Cleanup dependent records first to avoid FK constraint errors.
    orders_query = db.query(Order).filter(Order.bot_config_id == config_id)
    orders_count = orders_query.count()
    if orders_count > 0:
        orders_query.delete(synchronize_session=False)

    db.query(BotStatus).filter(BotStatus.bot_config_id == config_id).delete(synchronize_session=False)
    
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
    
    logger.info(f"Bot config deleted: {config.id} - {config.name} (deleted {orders_count} related orders)")
    return None


from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
import logging

from app.database import get_db
from app.models.order import Order
from app.schemas.order import OrderResponse, OrderHistoryFilter, OrderUpdate
from app.core.security import verify_token
from app.services.activity_log_service import activity_log_service
from app.exceptions.error_code import ErrorCode
from app.exceptions.error_exception import ErrorException
from app.exceptions.logical_exception import NotFoundException, BadRequestException
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/history", response_model=List[OrderResponse])
async def get_order_history(
    bot_config_id: Optional[int] = Query(None),
    symbol: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    side: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Get order history with filtering
    Supports filtering by bot_config_id, symbol, status, side, and date range
    """
    try:
        query = db.query(Order)
        
        # Apply filters
        if bot_config_id:
            query = query.filter(Order.bot_config_id == bot_config_id)
        
        if symbol:
            query = query.filter(Order.symbol == symbol)
        
        if status:
            query = query.filter(Order.status == status)
        
        if side:
            query = query.filter(Order.side == side.lower())
        
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        
        if end_date:
            query = query.filter(Order.created_at <= end_date)
        
        # Order by created_at descending (newest first)
        query = query.order_by(Order.created_at.desc())
        
        # Apply pagination
        orders = query.offset(offset).limit(limit).all()
        
        # Ensure tp_levels is always a list and add bot_config_name
        from app.models.bot_config import BotConfig
        for order in orders:
            if order.tp_levels is None:
                order.tp_levels = []
            elif not isinstance(order.tp_levels, list):
                order.tp_levels = []
            
            # Load bot_config relationship and get name with exchange
            if order.bot_config:
                exchange = order.bot_config.exchange or order.exchange or "binance"
                order.bot_config_name = f"{exchange.capitalize()} - {order.bot_config.name}"
            else:
                # Fallback: query directly if relationship not loaded
                bot_config = db.query(BotConfig).filter(BotConfig.id == order.bot_config_id).first()
                if bot_config:
                    exchange = bot_config.exchange or order.exchange or "binance"
                    order.bot_config_name = f"{exchange.capitalize()} - {bot_config.name}"
                else:
                    exchange = order.exchange or "binance"
                    order.bot_config_name = f"{exchange.capitalize()} - Bot #{order.bot_config_id}"
        
        return orders
    except ErrorException:
        raise
    except Exception as e:
        logger.error(f"Error fetching order history: {e}", exc_info=True)
        raise ErrorException(
            error_code=ErrorCode.UNDEFINED_ERROR,
            message=f"Internal server error: {str(e)}"
        )


@router.get("/completed", response_model=List[OrderResponse])
async def get_completed_orders(
    bot_config_id: Optional[int] = Query(None),
    symbol: Optional[str] = Query(None),
    side: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách lệnh đã hoàn thành (filled hoặc closed)
    
    Lệnh đã hoàn thành bao gồm:
    - status = "filled" (đã khớp)
    - status = "closed" (đã đóng)
    """
    try:
        query = db.query(Order).filter(
            Order.status.in_(["filled", "closed"])
        )
        
        # Apply filters
        if bot_config_id:
            query = query.filter(Order.bot_config_id == bot_config_id)
        
        if symbol:
            query = query.filter(Order.symbol == symbol)
        
        if side:
            query = query.filter(Order.side == side.lower())
        
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        
        if end_date:
            query = query.filter(Order.created_at <= end_date)
        
        # Order by created_at descending (newest first)
        query = query.order_by(Order.created_at.desc())
        
        # Apply pagination
        orders = query.offset(offset).limit(limit).all()
        
        # Ensure tp_levels is always a list and add bot_config_name
        from app.models.bot_config import BotConfig
        for order in orders:
            if order.tp_levels is None:
                order.tp_levels = []
            elif not isinstance(order.tp_levels, list):
                order.tp_levels = []
            
            # Load bot_config relationship and get name with exchange
            if order.bot_config:
                exchange = order.bot_config.exchange or order.exchange or "binance"
                order.bot_config_name = f"{exchange.capitalize()} - {order.bot_config.name}"
            else:
                # Fallback: query directly if relationship not loaded
                bot_config = db.query(BotConfig).filter(BotConfig.id == order.bot_config_id).first()
                if bot_config:
                    exchange = bot_config.exchange or order.exchange or "binance"
                    order.bot_config_name = f"{exchange.capitalize()} - {bot_config.name}"
                else:
                    exchange = order.exchange or "binance"
                    order.bot_config_name = f"{exchange.capitalize()} - Bot #{order.bot_config_id}"
        
        return orders
    except ErrorException:
        raise
    except Exception as e:
        logger.error(f"Error fetching completed orders: {e}", exc_info=True)
        raise ErrorException(
            error_code=ErrorCode.UNDEFINED_ERROR,
            message=f"Internal server error: {str(e)}"
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get a specific order by ID"""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise NotFoundException(message="Order not found")
        
        # Ensure tp_levels is always a list and add bot_config_name
        if order.tp_levels is None:
            order.tp_levels = []
        elif not isinstance(order.tp_levels, list):
            order.tp_levels = []
        
        # Load bot_config relationship and get name with exchange
        if order.bot_config:
            exchange = order.bot_config.exchange or order.exchange or "binance"
            order.bot_config_name = f"{exchange.capitalize()} - {order.bot_config.name}"
        else:
            # Fallback: query directly if relationship not loaded
            from app.models.bot_config import BotConfig
            bot_config = db.query(BotConfig).filter(BotConfig.id == order.bot_config_id).first()
            if bot_config:
                exchange = bot_config.exchange or order.exchange or "binance"
                order.bot_config_name = f"{exchange.capitalize()} - {bot_config.name}"
            else:
                exchange = order.exchange or "binance"
                order.bot_config_name = f"{exchange.capitalize()} - Bot #{order.bot_config_id}"
        
        return order
    except ErrorException:
        raise
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {e}", exc_info=True)
        raise ErrorException(
            error_code=ErrorCode.UNDEFINED_ERROR,
            message=f"Internal server error: {str(e)}"
        )


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Update a pending limit order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise NotFoundException(message="Order not found")

    order_status = (order.status or "").lower()
    order_type = (order.order_type or "").lower()

    if order_status in ["filled", "closed", "cancelled", "error"]:
        raise BadRequestException(message="Order status does not allow editing")

    if order_status != "pending" or order_type != "limit":
        raise BadRequestException(message="Only pending limit orders can be edited")

    update_data = order_data.dict(exclude_unset=True)
    if not update_data:
        raise BadRequestException(message="No fields provided for update")

    if "amount" in update_data and update_data["amount"] <= 0:
        raise BadRequestException(message="Amount must be greater than 0")
    if "price" in update_data and update_data["price"] <= 0:
        raise BadRequestException(message="Price must be greater than 0")
    if "stop_loss_price" in update_data and update_data["stop_loss_price"] < 0:
        raise BadRequestException(message="Stop loss must be greater than or equal to 0")
    if "take_profit_price" in update_data and update_data["take_profit_price"] < 0:
        raise BadRequestException(message="Take profit must be greater than or equal to 0")

    if "tp_levels" in update_data:
        tp_levels = update_data["tp_levels"]
        if tp_levels is None:
            update_data["tp_levels"] = []
        elif not isinstance(tp_levels, list):
            raise BadRequestException(message="TP levels must be a list")

    changes = {}
    for field, value in update_data.items():
        old_value = getattr(order, field)
        if old_value != value:
            changes[field] = {"from": old_value, "to": value}
            setattr(order, field, value)

    if not changes:
        raise BadRequestException(message="No changes detected")

    db.commit()
    db.refresh(order)

    activity_log_service.log_activity(
        db=db,
        level="info",
        category="order",
        message=f"Order updated by {username}",
        bot_config_id=order.bot_config_id,
        order_id=order.id,
        details=changes
    )

    return order


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """List all orders"""
    try:
        orders = db.query(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        
        # Ensure tp_levels is always a list and add bot_config_name
        from app.models.bot_config import BotConfig
        for order in orders:
            if order.tp_levels is None:
                order.tp_levels = []
            elif not isinstance(order.tp_levels, list):
                order.tp_levels = []
            
            # Load bot_config relationship and get name with exchange
            if order.bot_config:
                exchange = order.bot_config.exchange or order.exchange or "binance"
                order.bot_config_name = f"{exchange.capitalize()} - {order.bot_config.name}"
            else:
                # Fallback: query directly if relationship not loaded
                bot_config = db.query(BotConfig).filter(BotConfig.id == order.bot_config_id).first()
                if bot_config:
                    exchange = bot_config.exchange or order.exchange or "binance"
                    order.bot_config_name = f"{exchange.capitalize()} - {bot_config.name}"
                else:
                    exchange = order.exchange or "binance"
                    order.bot_config_name = f"{exchange.capitalize()} - Bot #{order.bot_config_id}"
        
        return orders
    except ErrorException:
        raise
    except Exception as e:
        logger.error(f"Error listing orders: {e}", exc_info=True)
        raise ErrorException(
            error_code=ErrorCode.UNDEFINED_ERROR,
            message=f"Internal server error: {str(e)}"
        )

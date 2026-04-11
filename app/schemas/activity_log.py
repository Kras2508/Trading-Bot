from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class ActivityLogResponse(BaseModel):
    id: int
    bot_config_id: Optional[int]
    order_id: Optional[int]
    level: str
    category: str
    message: str
    details: Optional[Dict]
    source_ip: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


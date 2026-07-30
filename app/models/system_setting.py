from sqlalchemy import Column, Integer, String, Boolean, Text
from app.database import Base


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    webhook_passphrase = Column(String(255), default="")
    enable_ip_whitelist = Column(Boolean, default=False)
    allowed_ips = Column(Text, default="")

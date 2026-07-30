from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List, Union
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Trading Bot Backend"
    DEBUG: Union[bool, str] = Field(default=False)
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./trading_bot.db")
    
    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = Field(default=["*"])
    
    # IP Whitelist
    ENABLE_IP_WHITELIST: Union[bool, str] = Field(default=False)
    ALLOWED_IPS: Union[List[str], str] = Field(default_factory=list)
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(default="")
    TELEGRAM_CHAT_ID: str = Field(default="")
    ENABLE_TELEGRAM: Union[bool, str] = Field(default=False)
    
    # Exchange API (encrypted in DB, these are defaults)
    DEFAULT_EXCHANGE: str = "binance"
    
    # Webhook
    WEBHOOK_PASSPHRASE: str = Field(default="")
    
    # Encryption
    ENCRYPTION_KEY: str = Field(default="your-32-byte-encryption-key-change-this")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields from .env
    )
    
    def model_post_init(self, __context):
        # Convert string booleans from .env
        if isinstance(self.DEBUG, str):
            self.DEBUG = self.DEBUG.lower() == "true"
        if isinstance(self.ENABLE_IP_WHITELIST, str):
            self.ENABLE_IP_WHITELIST = self.ENABLE_IP_WHITELIST.lower() == "true"
        if isinstance(self.ENABLE_TELEGRAM, str):
            self.ENABLE_TELEGRAM = self.ENABLE_TELEGRAM.lower() == "true"
        
        # Parse ALLOWED_IPS if it's a string
        if isinstance(self.ALLOWED_IPS, str):
            self.ALLOWED_IPS = [ip.strip() for ip in self.ALLOWED_IPS.split(",") if ip.strip()]
        
        # Parse CORS_ORIGINS if it's a string
        if isinstance(self.CORS_ORIGINS, str):
            try:
                import json
                self.CORS_ORIGINS = json.loads(self.CORS_ORIGINS)
            except:
                self.CORS_ORIGINS = [self.CORS_ORIGINS]


settings = Settings()


import logging
from typing import Optional
from app.core.config import settings
import requests

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for sending Telegram notifications"""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.enabled = settings.ENABLE_TELEGRAM and self.bot_token and self.chat_id
        
        if self.enabled:
            logger.info("Telegram notifications enabled")
        else:
            logger.warning("Telegram notifications disabled or not configured")
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """Send a message to Telegram"""
        if not self.enabled:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def send_bot_status(self, bot_name: str, status: str, details: Optional[str] = None):
        """Send bot status update"""
        message = f"🤖 <b>Bot Status Update</b>\n\n"
        message += f"Bot: <b>{bot_name}</b>\n"
        message += f"Status: <b>{status}</b>\n"
        if details:
            message += f"Details: {details}"
        return self.send_message(message)
    
    def send_order_notification(self, order_info: dict):
        """Send order notification"""
        message = f"📊 <b>Order Notification</b>\n\n"
        message += f"Symbol: <b>{order_info.get('symbol')}</b>\n"
        message += f"Side: <b>{order_info.get('side').upper()}</b>\n"
        message += f"Amount: <b>{order_info.get('amount')}</b>\n"
        message += f"Status: <b>{order_info.get('status')}</b>\n"
        if order_info.get('price'):
            message += f"Price: <b>{order_info.get('price')}</b>\n"
        if order_info.get('error'):
            message += f"❌ Error: {order_info.get('error')}"
        return self.send_message(message)
    
    def send_error_alert(self, bot_name: str, error_message: str):
        """Send error alert"""
        message = f"⚠️ <b>Error Alert</b>\n\n"
        message += f"Bot: <b>{bot_name}</b>\n"
        message += f"Error: <code>{error_message}</code>"
        return self.send_message(message)
    
    def send_bot_paused_alert(self, bot_name: str, reason: Optional[str] = None):
        """Send alert when bot is paused"""
        message = f"⏸️ <b>Bot Paused</b>\n\n"
        message += f"Bot: <b>{bot_name}</b>\n"
        if reason:
            message += f"Reason: {reason}"
        return self.send_message(message)


telegram_service = TelegramService()


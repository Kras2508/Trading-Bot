from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import check_ip_whitelist
from app.core.config import settings
from app.utils.response import error_response
import logging

logger = logging.getLogger(__name__)


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """Middleware to check IP whitelist"""
    
    async def dispatch(self, request: Request, call_next):
        if settings.ENABLE_IP_WHITELIST:
            client_ip = request.client.host
            
            # Check X-Forwarded-For header for proxied requests
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                client_ip = forwarded_for.split(",")[0].strip()
            
            if not check_ip_whitelist(client_ip):
                logger.warning(f"IP {client_ip} not in whitelist")
                return error_response(
                    message="IP address not allowed",
                    status_code=status.HTTP_403_FORBIDDEN
                )
        
        response = await call_next(request)
        return response


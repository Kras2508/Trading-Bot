from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import logging

from app.utils.response import error_response
from app.exceptions.error_exception import ErrorException

from app.database import engine, Base
from app.routers import auth, config, webhook, orders, monitoring, trading
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.middleware import IPWhitelistMiddleware

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def init_system_settings():
    from app.database import SessionLocal
    from app.models.system_setting import SystemSetting
    from app.core.config import settings
    import secrets
    
    db = SessionLocal()
    try:
        existing = db.query(SystemSetting).first()
        if not existing:
            allowed_ips_str = ",".join(settings.ALLOWED_IPS) if isinstance(settings.ALLOWED_IPS, list) else str(settings.ALLOWED_IPS)
            
            passphrase = settings.WEBHOOK_PASSPHRASE
            if not passphrase or passphrase.strip() == "":
                passphrase = secrets.token_hex(16)
                logger.info(f"Generated secure default Webhook Passphrase: {passphrase}")
                
            db_settings = SystemSetting(
                id=1,
                webhook_passphrase=passphrase,
                enable_ip_whitelist=settings.ENABLE_IP_WHITELIST,
                allowed_ips=allowed_ips_str
            )
            db.add(db_settings)
            db.commit()
            logger.info("Default system settings initialized in DB")
    except Exception as e:
        logger.error(f"Failed to initialize system settings: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    init_system_settings()
    
    # Start background order status sync loop
    import asyncio
    from app.services.order_sync_worker import run_order_sync_loop
    sync_task = asyncio.create_task(run_order_sync_loop())
    
    yield
    # Shutdown
    logger.info("Shutting down application...")
    sync_task.cancel()
    try:
        await sync_task
    except asyncio.CancelledError:
        logger.info("Background order sync task cancelled successfully")


app = FastAPI(
    title="Trading Bot Backend API",
    description="Backend API for Trading Bot Management System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# IP Whitelist middleware (if enabled)
if settings.ENABLE_IP_WHITELIST:
    app.add_middleware(IPWhitelistMiddleware)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if 400 <= exc.status_code < 500:
        logger.warning(f"HTTP client exception: {exc.detail} (Status: {exc.status_code})")
    else:
        logger.error(f"HTTP server exception: {exc.detail} (Status: {exc.status_code})")
    return error_response(
        message=exc.detail,
        status_code=exc.status_code
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return error_response(
        message="Request validation failed",
        error_details=exc.errors(),
        status_code=422
    )


@app.exception_handler(ErrorException)
async def error_exception_handler(request: Request, exc: ErrorException):
    status_code = exc.error_code.status_code
    if 400 <= status_code < 500:
        logger.warning(f"Logical error ({exc.error_code.name}): {exc.message} (Code: {exc.error_code.code}, Status: {status_code})")
    else:
        logger.error(f"System error ({exc.error_code.name}): {exc.message} (Code: {exc.error_code.code}, Status: {status_code})")
        
    return error_response(
        message=exc.message,
        error_details=exc.error_details,
        status_code=status_code,
        error_code=exc.error_code.code
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return error_response(
        message="Internal server error",
        error_details=None,
        status_code=500
    )


@app.get("/")
async def root():
    return {
        "message": "Trading Bot Backend API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Compatibility endpoints to reduce 404 errors
@app.post("/api/login")
async def api_login_compat():
    """Compatibility endpoint - redirect to /api/auth/login"""
    return JSONResponse(
        status_code=301,
        content={"detail": "Please use POST /api/auth/login instead"}
    )


@app.post("/api/health")
@app.get("/api/health")
async def api_health_compat():
    """Compatibility endpoint for /api/health"""
    return {"status": "healthy"}


@app.post("/api/version")
@app.get("/api/version")
async def api_version_compat():
    """Compatibility endpoint for /api/version"""
    return {
        "version": "1.0.0",
        "message": "Trading Bot Backend API"
    }


@app.post("/api/")
@app.get("/api/")
async def api_root_compat():
    """Compatibility endpoint for /api/"""
    return {
        "message": "Trading Bot Backend API",
        "version": "1.0.0",
        "status": "running"
    }


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(config.router, prefix="/api/config", tags=["Configuration"])
app.include_router(webhook.router, prefix="/api/webhook", tags=["Webhook"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["Monitoring"])
app.include_router(trading.router, prefix="/api/trading", tags=["Trading"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Cho phép truy cập từ bên ngoài


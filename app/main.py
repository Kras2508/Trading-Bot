from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.database import engine, Base
from app.routers import auth, config, webhook, orders, monitoring, trading
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.middleware import IPWhitelistMiddleware

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    yield
    # Shutdown
    logger.info("Shutting down application...")


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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
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


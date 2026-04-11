"""
Script to run the FastAPI application
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Cho phép truy cập từ bên ngoài
        port=8000,
        reload=True,
        log_level="info"
    )


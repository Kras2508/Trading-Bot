"""
Script to run the FastAPI application on port 80
NOTE: Requires Administrator privileges on Windows
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Cho phép truy cập từ bên ngoài
        port=80,  # Port 80 - yêu cầu quyền Administrator
        reload=True,
        log_level="info"
    )


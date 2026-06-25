from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Any, Optional
from fastapi import status

def success_response(data: Any = None, message: str = "Success", status_code: int = status.HTTP_200_OK):
    """
    Tạo response JSON chuẩn hóa cho thành công
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": jsonable_encoder(data)
        }
    )

def error_response(message: str = "Error", error_details: Any = None, status_code: int = status.HTTP_400_BAD_REQUEST):
    """
    Tạo response JSON chuẩn hóa cho lỗi
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "errors": jsonable_encoder(error_details)
        }
    )

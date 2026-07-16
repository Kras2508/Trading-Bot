from typing import Any, Optional
from app.exceptions.error_code import ErrorCode

class ErrorException(Exception):
    """
    Exception cơ bản chuẩn hóa cho toàn hệ thống
    """
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        error_details: Optional[Any] = None
    ):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.error_details = error_details

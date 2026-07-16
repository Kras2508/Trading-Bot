from typing import Any, Optional
from app.exceptions.error_code import ErrorCode
from app.utils.error_parser import clean_error_message

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
        cleaned_msg = clean_error_message(message)
        super().__init__(cleaned_msg)
        self.error_code = error_code
        self.message = cleaned_msg
        self.error_details = error_details

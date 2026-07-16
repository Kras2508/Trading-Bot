from typing import Any, Optional
from app.exceptions.error_code import ErrorCode
from app.exceptions.error_exception import ErrorException

class LogicalException(ErrorException):
    """
    Exception dùng cho các lỗi logic nghiệp vụ giao dịch / thao tác (4xx)
    """
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.BAD_REQUEST,
        error_details: Optional[Any] = None
    ):
        super().__init__(error_code=error_code, message=message, error_details=error_details)
        
class ExchangeException(LogicalException):
    """
    Exception chuyên biệt cho lỗi tương tác với sàn giao dịch (Binance/CCXT)
    """
    def __init__(
        self,
        message: str,
        error_details: Optional[Any] = None
    ):
        from app.utils.error_parser import clean_error_message
        cleaned_msg = clean_error_message(message)
        super().__init__(
            message=cleaned_msg,
            error_code=ErrorCode.EXCHANGE_ERROR,
            error_details=error_details
        )

class NotFoundException(ErrorException):
    """Exception cho lỗi không tìm thấy tài nguyên (HTTP 404)"""
    def __init__(self, message: str, error_details: Optional[Any] = None):
        super().__init__(error_code=ErrorCode.NOT_FOUND, message=message, error_details=error_details)

class UnauthorizedException(ErrorException):
    """Exception cho lỗi chưa đăng nhập / sai token (HTTP 401)"""
    def __init__(self, message: str, error_details: Optional[Any] = None):
        super().__init__(error_code=ErrorCode.UNAUTHORIZED, message=message, error_details=error_details)

class ForbiddenException(ErrorException):
    """Exception cho lỗi không có quyền truy cập (HTTP 403)"""
    def __init__(self, message: str, error_details: Optional[Any] = None):
        super().__init__(error_code=ErrorCode.FORBIDDEN, message=message, error_details=error_details)

class ValidationException(ErrorException):
    """Exception cho lỗi xác thực dữ liệu đầu vào (HTTP 422)"""
    def __init__(self, message: str, error_details: Optional[Any] = None):
        super().__init__(error_code=ErrorCode.VALIDATION_ERROR, message=message, error_details=error_details)

class BadRequestException(LogicalException):
    """Exception cho lỗi yêu cầu không hợp lệ (HTTP 400)"""
    def __init__(self, message: str, error_details: Optional[Any] = None):
        super().__init__(message=message, error_code=ErrorCode.BAD_REQUEST, error_details=error_details)

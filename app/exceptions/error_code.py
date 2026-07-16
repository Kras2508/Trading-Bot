from enum import Enum

class ErrorCode(Enum):
    UNDEFINED_ERROR = '1|500'
    VALIDATION_ERROR = '2|422'
    NOT_FOUND = '3|404'
    UNAUTHORIZED = '4|401'
    FORBIDDEN = '5|403'
    BAD_REQUEST = '6|400'
    
    # Custom business/trading error codes
    EXCHANGE_ERROR = '100|400'
    DUPLICATE_ORDER = '101|400'
    INSUFFICIENT_BALANCE = '102|400'

    @property
    def code(self) -> int:
        """Trả về mã lỗi số nội bộ (Internal Error Code)"""
        return int(self.value.split('|')[0])

    @property
    def status_code(self) -> int:
        """Trả về mã trạng thái HTTP tương ứng"""
        return int(self.value.split('|')[1])

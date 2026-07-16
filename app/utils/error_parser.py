import re
import json

def clean_error_message(msg: str) -> str:
    """
    Chuẩn hóa thông điệp lỗi từ exchange (CCXT/Binance) và loại bỏ các tiền tố (prefixes) bị lồng ghép nhiều lớp.
    Ví dụ: 
    - 'Failed to place order: binance {"code":-1013,"msg":"Filter failure: NOTIONAL"}' -> 'binance: Filter failure: NOTIONAL'
    - 'Place order error: Failed to place order: binance {"code":-2008,"msg":"Invalid Api-Key ID."}' -> 'binance: Invalid Api-Key ID.'
    """
    if not msg:
        return "Unknown error"
        
    msg_str = str(msg)
    
    # 1. Tìm đoạn JSON trong chuỗi lỗi (thường do CCXT/Binance trả về)
    match = re.search(r'(\{.*\})', msg_str)
    if match:
        try:
            json_str = match.group(1)
            err_data = json.loads(json_str)
            if isinstance(err_data, dict) and "msg" in err_data:
                clean_msg = err_data["msg"]
                prefix = "binance: " if "binance" in msg_str.lower() else ""
                return f"{prefix}{clean_msg}"
        except Exception:
            pass

    # 2. Xử lý loại bỏ các cụm prefix lặp đi lặp lại do bắt lỗi lồng nhau
    prefixes = [
        "Place order error:",
        "Failed to place order:",
        "Failed to close order:",
        "Webhook error:"
    ]
    
    changed = True
    while changed:
        changed = False
        msg_str = msg_str.strip()
        for p in prefixes:
            if msg_str.lower().startswith(p.lower()):
                msg_str = msg_str[len(p):].strip()
                changed = True
                
    if not msg_str:
        return "Unknown error"
        
    return msg_str

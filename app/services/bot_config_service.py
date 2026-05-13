import re
from typing import Any, Dict, Iterable, Optional

from fastapi import HTTPException


ALLOWED_EXCHANGES = {
    "binance",
    "bitget",
    "okx",
    "bybit",
    "gateio",
    "kucoin",
    "huobi",
    "coinbasepro",
    "kraken",
    "bitfinex"
}

SYMBOL_PATTERN = re.compile(r"^[A-Za-z0-9]+(\/[A-Za-z0-9]+)?(\.D)?$")


def _normalize_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(normalized):
        raise HTTPException(status_code=400, detail="Symbol format is invalid")
    return normalized


def _normalize_exchange(exchange: str) -> str:
    normalized = exchange.strip().lower()
    if normalized not in ALLOWED_EXCHANGES:
        raise HTTPException(status_code=400, detail="Exchange is not supported")
    return normalized


def _validate_non_negative(value: Optional[float], field_name: str) -> None:
    if value is None:
        return
    if value < 0:
        raise HTTPException(status_code=400, detail=f"{field_name} must be greater than or equal to 0")


def _normalize_tp_levels(tp_levels: Optional[Iterable[Any]]) -> Optional[list]:
    if tp_levels is None:
        return None

    normalized = []
    total_close = 0.0

    for level in tp_levels:
        if hasattr(level, "model_dump"):
            data = level.model_dump()
        elif hasattr(level, "dict"):
            data = level.dict()
        else:
            data = dict(level)

        percent = float(data.get("percent", 0))
        close_percent = float(data.get("close_percent", 0))

        if percent < 0:
            raise HTTPException(status_code=400, detail="TP percent must be greater than or equal to 0")
        if close_percent < 0:
            raise HTTPException(status_code=400, detail="TP close_percent must be greater than or equal to 0")

        total_close += close_percent
        normalized.append({"percent": percent, "close_percent": close_percent})

    if total_close > 100:
        raise HTTPException(status_code=400, detail="Total close_percent in tp_levels cannot exceed 100")

    return normalized


def _validate_trailing(enable_trailing: bool,
                       trailing_type: Optional[str],
                       trailing_percent: Optional[float],
                       trailing_atr_multiplier: Optional[float],
                       trailing_atr_period: Optional[int]) -> None:
    if not enable_trailing:
        return

    if trailing_type == "percent":
        if trailing_percent is None or trailing_percent <= 0:
            raise HTTPException(status_code=400, detail="Trailing percent must be greater than 0")
    elif trailing_type == "atr":
        if trailing_atr_multiplier is None or trailing_atr_multiplier <= 0:
            raise HTTPException(status_code=400, detail="ATR multiplier must be greater than 0")
        if trailing_atr_period is None or trailing_atr_period < 1:
            raise HTTPException(status_code=400, detail="ATR period must be at least 1")
    else:
        raise HTTPException(status_code=400, detail="Trailing type is invalid")


def validate_create_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(payload)

    normalized["symbol"] = _normalize_symbol(normalized["symbol"])
    normalized["exchange"] = _normalize_exchange(normalized["exchange"])

    _validate_non_negative(normalized.get("stop_loss_percent"), "Stop loss percent")
    _validate_non_negative(normalized.get("take_profit_percent"), "Take profit percent")
    _validate_non_negative(normalized.get("trailing_percent"), "Trailing percent")
    _validate_non_negative(normalized.get("trailing_atr_multiplier"), "ATR multiplier")

    tp_levels = _normalize_tp_levels(normalized.get("tp_levels"))
    if tp_levels is not None:
        normalized["tp_levels"] = tp_levels

    trading_mode = normalized.get("trading_mode")
    leverage = normalized.get("leverage")
    if trading_mode == "spot" and leverage != 1:
        raise HTTPException(status_code=400, detail="Leverage must be 1 for spot trading")

    _validate_trailing(
        normalized.get("enable_trailing", False),
        normalized.get("trailing_type"),
        normalized.get("trailing_percent"),
        normalized.get("trailing_atr_multiplier"),
        normalized.get("trailing_atr_period")
    )

    return normalized


def validate_update_payload(update_data: Dict[str, Any], config: Any) -> Dict[str, Any]:
    normalized = dict(update_data)

    if "symbol" in normalized and normalized["symbol"] is not None:
        normalized["symbol"] = _normalize_symbol(normalized["symbol"])

    if "exchange" in normalized and normalized["exchange"] is not None:
        normalized["exchange"] = _normalize_exchange(normalized["exchange"])

    _validate_non_negative(normalized.get("stop_loss_percent"), "Stop loss percent")
    _validate_non_negative(normalized.get("take_profit_percent"), "Take profit percent")
    _validate_non_negative(normalized.get("trailing_percent"), "Trailing percent")
    _validate_non_negative(normalized.get("trailing_atr_multiplier"), "ATR multiplier")

    tp_levels = _normalize_tp_levels(normalized.get("tp_levels"))
    if tp_levels is not None:
        normalized["tp_levels"] = tp_levels

    trading_mode = normalized.get("trading_mode", config.trading_mode)
    leverage = normalized.get("leverage", config.leverage)
    if trading_mode == "spot" and leverage != 1:
        raise HTTPException(status_code=400, detail="Leverage must be 1 for spot trading")

    enable_trailing = normalized.get("enable_trailing", config.enable_trailing)
    _validate_trailing(
        enable_trailing,
        normalized.get("trailing_type", config.trailing_type),
        normalized.get("trailing_percent", config.trailing_percent),
        normalized.get("trailing_atr_multiplier", config.trailing_atr_multiplier),
        normalized.get("trailing_atr_period", config.trailing_atr_period)
    )

    return normalized

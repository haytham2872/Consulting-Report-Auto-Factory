"""Shared rounding and formatting helpers to keep artifacts consistent."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


def _quantize(value: float | int | Decimal, places: int) -> Decimal:
    dec_value = Decimal(str(value))
    quantizer = Decimal("1." + ("0" * places))
    return dec_value.quantize(quantizer, rounding=ROUND_HALF_UP)


def format_currency(value: float | int | Decimal, currency_symbol: str = "$", places: int = 2) -> str:
    """Format a currency value using half-up rounding."""
    rounded = _quantize(value, places)
    return f"{currency_symbol}{rounded:,.{places}f}"


def format_percent(value: float | int | Decimal, places: int = 1) -> str:
    """Format a percentage value using half-up rounding."""
    rounded = _quantize(value * 100, places)
    return f"{rounded:.{places}f}%"


def format_integer(value: float | int | Decimal) -> str:
    """Format an integer with thousand separators after rounding."""
    rounded = int(_quantize(value, 0))
    return f"{rounded:,}"


def register_jinja_filters(env) -> None:
    env.filters["currency"] = format_currency
    env.filters["percent"] = format_percent
    env.filters["int"] = format_integer

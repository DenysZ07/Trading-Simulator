from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class AssetClass(Enum):
    EQUITY = "equity"


class Interval(Enum):
    DAY = "1day"


@dataclass(frozen=True)
class Candle:
    timestamp: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal = Decimal("0")


@dataclass(frozen=True)
class Quote:
    price: Decimal
    timestamp: int


@dataclass(frozen=True)
class Instrument:
    symbol: str
    display_name: str
    asset_class: AssetClass
    quote_currency: str = "USD"
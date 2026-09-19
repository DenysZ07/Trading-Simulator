from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


class Side(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"


@dataclass(frozen=True)
class Order:
    symbol: str
    side: Side
    quantity: int
    order_type: OrderType
    limit_price: Decimal | None = None


@dataclass(frozen=True)
class Trade:
    symbol: str
    side: Side
    quantity: int
    fill_price: Decimal
    timestamp: int
    commission: Decimal
    slippage: Decimal



@dataclass(frozen=True)
class Lot: 
    quantity: int 
    price: Decimal
    timestamp: int 

@dataclass
class Position: 
    symbol: str 
    lots: list[Lot] = field(default_factory=list)
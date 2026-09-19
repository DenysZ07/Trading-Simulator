from decimal import Decimal
from .orders import Side

# Trading 212 doesn't have commission charges for stocks and ETFs
COMMISSION_BPS = Decimal("0") 

# Large cap US equities usually quote between 1-5bps
SPREAD_BPS = Decimal("2") 

# Typically between 0-5bps for retail sized orders. 
# It's fixed right now but later will scale based on order size and candle volume.
SLIPPAGE_BPS = Decimal("2") 


def get_cost(side: Side, price: Decimal) -> Decimal:

    total = ((SPREAD_BPS / 2) + SLIPPAGE_BPS) / 10000

    if side == Side.BUY:
        return price * (1 + total)
    
    elif side == Side.SELL:
        return price * (1 - total)       

    else: 
        raise ValueError(f"unknown side: {side}")
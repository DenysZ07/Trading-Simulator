from decimal import Decimal
from .orders import Portfolio, Side

def realised_pnl(portfolio: Portfolio) -> Decimal:
    total = Decimal("0")


    for trade in portfolio.trades: 
        if trade.side == Side.SELL: 
            proceeds = trade.fill_price * trade.quantity
            total += proceeds - trade.cost_basis

    return total 


def unrealised_pnl(portfolio: Portfolio, prices: dict[str, Decimal]) -> Decimal:
    total = Decimal("0")

    for symbol, position in portfolio.positions.items():
        current_price = prices[symbol]

        for lot in position.lots: 
            cost = lot.price * lot.quantity
            value = current_price * lot.quantity
            total += value - cost


    return total



    
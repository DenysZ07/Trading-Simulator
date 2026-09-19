from .costs import get_cost, COMMISSION_BPS, SPREAD_BPS, SLIPPAGE_BPS
from .orders import Side, Portfolio, Order, Trade, Position, Lot
from .exceptions import OrderRejected
from decimal import Decimal


def fill_order(portfolio: Portfolio, order: Order, price: Decimal, timestamp: int) -> Trade:

    fill_price = get_cost(order.side, price) 
    total_cost = fill_price * order.quantity

    if order.side == Side.BUY: 

        if total_cost > portfolio.cash:
            raise OrderRejected(f"need {total_cost}, have {portfolio.cash}")

        portfolio.cash -= total_cost

        position = portfolio.positions.setdefault(order.symbol, Position(order.symbol))
        position.lots.append(Lot(order.quantity, fill_price, timestamp))

        trade = Trade(
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            fill_price=fill_price,
            timestamp=timestamp,
            commission=(COMMISSION_BPS / 10000)*price*order.quantity,
            spread=((SPREAD_BPS/2) / 10000)*price*order.quantity,
            slippage=(SLIPPAGE_BPS / 10000)*price*order.quantity,
        )


        portfolio.trades.append(trade)
        return trade

    elif order.side == Side.SELL:
        raise NotImplementedError







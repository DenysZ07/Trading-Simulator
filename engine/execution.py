from .costs import get_cost, COMMISSION_BPS, SPREAD_BPS, SLIPPAGE_BPS
from .orders import Side, Portfolio, Order, Trade, Position, Lot, OrderType
from .exceptions import OrderRejected
from decimal import Decimal


def fill_order(portfolio: Portfolio, order: Order, price: Decimal, timestamp: int) -> Trade:

    fill_price = get_cost(order.side, price) 
    total_cost = fill_price * order.quantity


    if order.order_type == OrderType.LIMIT:

        if order.side == Side.BUY and fill_price > order.limit_price:
            raise OrderRejected(f"The fill price: ${fill_price}, is above the order limit of ${order.limit_price}")
        elif order.side == Side.SELL and fill_price < order.limit_price:
            raise OrderRejected(f"The fill price: ${fill_price}, is below the order limit of ${order.limit_price}")



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
        position = portfolio.positions.get(order.symbol)

        held = sum(lot.quantity for lot in position.lots) if position else 0 

        if held < order.quantity:
            raise OrderRejected(f"holding {held}, tried to sell {order.quantity}")

        remaining = order.quantity
        cost_basis = Decimal("0")


        while remaining > 0:
            lot = position.lots[0]

            if lot.quantity <= remaining:
                cost_basis += lot.price * lot.quantity
                remaining -= lot.quantity
                position.lots.pop(0)

            else:
                cost_basis += lot.price *  remaining
                position.lots[0] = Lot(lot.quantity - remaining, lot.price, lot.timestamp)
                remaining = 0



        portfolio.cash += total_cost

        trade = Trade(
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            fill_price=fill_price,
            timestamp=timestamp,
            commission=(COMMISSION_BPS / 10000)*price*order.quantity,
            spread=((SPREAD_BPS/2) / 10000)*price*order.quantity,
            slippage=(SLIPPAGE_BPS / 10000)*price*order.quantity,
            cost_basis=cost_basis,
        )


        portfolio.trades.append(trade)
        return trade
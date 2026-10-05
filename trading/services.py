from decimal import Decimal
from engine.orders import Lot, Portfolio, Position, Side, Trade
from . import models


def load_portfolio(db_portfolio: models.Portfolio) -> Portfolio:
    portfolio = Portfolio(cash=db_portfolio.cash)

    for db_position in db_portfolio.positions.all():
        position = Position(db_position.symbol)


        for db_lot in db_position.lots.all().order_by("timestamp", "id"):
            position.lots.append(Lot(db_lot.quantity, db_lot.price, db_lot.timestamp))


        portfolio.positions[db_position.symbol] = position


    for db_trade in db_portfolio.trades.all().order_by("timestamp", "id"):
        portfolio.trades.append(Trade(
            symbol=db_trade.symbol,
            side=Side(db_trade.side),
            quantity=db_trade.quantity,
            fill_price=db_trade.fill_price,
            timestamp=db_trade.timestamp,
            commission=db_trade.commission,
            spread=db_trade.spread,
            slippage=db_trade.slippage,
            cost_basis=db_trade.cost_basis,
        ))

    return portfolio
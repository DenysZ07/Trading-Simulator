from decimal import Decimal
from engine.orders import Lot, Portfolio, Position, Side, Trade
from . import models
from django.db import transaction
from django.conf import settings


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


def save_portfolio(db_portfolio: models.Portfolio, portfolio: Portfolio) -> None:

    with transaction.atomic():

        db_portfolio.cash = portfolio.cash
        db_portfolio.save()
        db_portfolio.positions.all().delete()

        for symbol, position in portfolio.positions.items():

            if not position.lots:
                continue 

            db_position = models.Position.objects.create(portfolio=db_portfolio, symbol=symbol)


            for lot in position.lots:
                models.Lot.objects.create(
                    position=db_position,
                    quantity=lot.quantity, 
                    price=lot.price,
                    timestamp=lot.timestamp,
                )
        stored = db_portfolio.trades.count()

        for trade in portfolio.trades[stored:]:
            models.Trade.objects.create(
                portfolio=db_portfolio,
                symbol=trade.symbol,
                side=trade.side.value,
                quantity=trade.quantity,
                fill_price=trade.fill_price,
                timestamp=trade.timestamp,
                commission=trade.commission,
                spread=trade.spread,
                slippage=trade.slippage,
                cost_basis=trade.cost_basis,
            )


def get_or_create_portfolio(request) -> models.Portfolio:
    if not request.session.session_key:
        request.session.create()

    db_portfolio, _ = models.Portfolio.objects.get_or_create(
        session_key=request.session.session_key,
        defaults={"cash": settings.STARTING_CASH},
    )

    return db_portfolio
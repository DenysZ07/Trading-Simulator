from decimal import Decimal
from engine.orders import Lot, Portfolio, Position, Side, Trade
from . import models
from django.db import transaction
from django.conf import settings
from engine.ledger import START_OF_CHAIN, serialise_trade, chain_digest


def to_engine_trade(db_trade: models.Trade) -> Trade:
    return Trade(
        symbol=db_trade.symbol,
        side=Side(db_trade.side),
        quantity=db_trade.quantity,
        fill_price=db_trade.fill_price,
        timestamp=db_trade.timestamp,
        commission=db_trade.commission,
        spread=db_trade.spread,
        slippage=db_trade.slippage,
        cost_basis=db_trade.cost_basis,
    )


def load_portfolio(db_portfolio: models.Portfolio) -> Portfolio:
    portfolio = Portfolio(cash=db_portfolio.cash)

    for db_position in db_portfolio.positions.all():
        position = Position(db_position.symbol)


        for db_lot in db_position.lots.all().order_by("timestamp", "id"):
            position.lots.append(Lot(db_lot.quantity, db_lot.price, db_lot.timestamp))


        portfolio.positions[db_position.symbol] = position


    for db_trade in db_portfolio.trades.all().order_by("timestamp", "id"):
        portfolio.trades.append(to_engine_trade(db_trade))

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

        head = db_portfolio.ledger_entries.order_by("-sequence").first()
        previous_digest = bytes.fromhex(head.digest) if head else START_OF_CHAIN
        sequence = head.sequence + 1 if head else 0

        for trade in portfolio.trades[stored:]:
            
            db_trade = models.Trade.objects.create(
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

            payload = serialise_trade(trade)
            digest = chain_digest(previous_digest, payload)

            models.LedgerEntry.objects.create(
                portfolio=db_portfolio,
                trade=db_trade,
                sequence=sequence,
                payload=payload.decode("utf-8"),
                previous_digest=previous_digest.hex(),
                digest=digest.hex(),
            )

            previous_digest = digest
            sequence += 1


def verify_ledger(db_portfolio: models.Portfolio) -> dict: 
    previous_digest = START_OF_CHAIN
    count = 0 

    for entry in db_portfolio.ledger_entries.all():
        payload = entry.payload.encode("utf-8")

        if serialise_trade(to_engine_trade(entry.trade)) != payload: 
            return {"intact": False, "sequence": entry.sequence, "failure": "content"}

        if chain_digest(bytes.fromhex(entry.previous_digest), payload).hex() != entry.digest:
            return {"intact": False, "sequence": entry.sequence, "failure": "digest"}

        if entry.previous_digest != previous_digest.hex():
            return {"intact": False, "sequence": entry.sequence, "failure": "link"}

        previous_digest = bytes.fromhex(entry.digest)
        count += 1

    return {"intact": True, "entries": count}


def get_or_create_portfolio(request) -> models.Portfolio:
    if not request.session.session_key:
        request.session.create()

    db_portfolio, _ = models.Portfolio.objects.get_or_create(
        session_key=request.session.session_key,
        defaults={"cash": settings.STARTING_CASH},
    )

    return db_portfolio
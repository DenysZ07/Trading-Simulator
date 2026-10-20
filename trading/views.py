import json 
from decimal import Decimal
from django.http import JsonResponse
from engine.exceptions import OrderRejected
from engine.orders import Order, OrderType, Side 
from . import services
from django.shortcuts import get_object_or_404
from marketdata.models import Candle, Instrument
from marketdata.providers.shapes import Interval
from engine.execution import fill_order
from engine.pnl import realised_pnl




def place_order(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body, parse_float=Decimal)

    symbol = data["symbol"].upper()
    side = Side(data["side"])
    quantity = int(data["quantity"])
    order_type = OrderType(data["order_type"])
    limit_price = Decimal(data["limit_price"]) if data.get("limit_price") else None

    db_portfolio = services.get_or_create_portfolio(request)
    portfolio = services.load_portfolio(db_portfolio)

    order = Order(symbol, side, quantity, order_type, limit_price)


    instrument = get_object_or_404(Instrument, symbol=symbol)

    candle = Candle.objects.filter(instrument=instrument, interval=Interval.DAY.value).order_by("-timestamp").first()


    try: 
        trade = fill_order(portfolio, order, candle.close, candle.timestamp)
    except OrderRejected as error: 
        return JsonResponse({"error": str(error)}, status=400)

    services.save_portfolio(db_portfolio, portfolio)


    return JsonResponse({
        "symbol": trade.symbol, 
        "side": trade.side.value,
        "quantity": trade.quantity,
        "fill_price": float(trade.fill_price),
    })



def portfolio_state(request):
    db_portfolio = services.get_or_create_portfolio(request)
    portfolio = services.load_portfolio(db_portfolio)

    prices = {}

    for symbol in portfolio.positions:
        candle = Candle.objects.filter(
            instrument__symbol=symbol,
            interval=Interval.DAY.value,
        ).order_by("-timestamp").first()

        prices[symbol] = candle.close


    positions = []
    holdings_value = Decimal("0")

    for symbol,position in portfolio.positions.items():
        quantity = sum(lot.quantity for lot in position.lots)
        cost = sum(lot.price * lot.quantity for lot in position.lots)

        value = prices[symbol] * quantity

        holdings_value += value

        positions.append({
            "symbol": symbol,
            "quantity": quantity,
            "average_cost": float(cost / quantity),
            "current_price": float(prices[symbol]),
            "value": float(value),
            "unrealised_pnl": float(value - cost),
        })


    return JsonResponse({
        "cash": float(portfolio.cash),
        "holdings_value": float(holdings_value),
        "total_value": float(portfolio.cash + holdings_value),
        "realised_pnl": float(realised_pnl(portfolio)),
        "positions": positions,
    })


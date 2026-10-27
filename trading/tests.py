from django.test import TestCase
import json
from decimal import Decimal
from marketdata.models import Candle, Instrument
from marketdata.providers.shapes import Interval
from . import services
from . import models
from engine.execution import fill_order
from engine.orders import Order, OrderType, Portfolio, Side


class PlaceOrderTests(TestCase):

    def setUp(self):
        self.instrument = Instrument.objects.create(
            symbol="AAPL",
            display_name="Apple Inc.",
            asset_class="equity",  
        )

        Candle.objects.create(
            instrument=self.instrument,
            interval=Interval.DAY.value,
            timestamp=1700000000,
            open=Decimal("100"),
            high=Decimal("105"),
            low=Decimal("99"),
            close=Decimal("100"),
            volume=Decimal("1000"),
        )

    def test_market_buy_succeeds(self):
        response = self.client.post(
            "/api/order/",
            json.dumps({
                "symbol": "AAPL",
                "side": "buy",
                "quantity": 2, 
                "order_type": "market",
            }),
            content_type="application/json"
        )
    
        self.assertEqual(response.status_code, 200)


class LedgerTests(TestCase):

    def setUp(self):
        self.db_portfolio = models.Portfolio.objects.create(
            session_key="ledger-test",
            cash=Decimal("100000"),
        )

        portfolio = Portfolio(cash=Decimal("100000"))

        fill_order(portfolio, Order("AAPL", Side.BUY, 1, OrderType.MARKET), Decimal("100"), 1700000000)
        fill_order(portfolio, Order("AAPL", Side.BUY, 1, OrderType.MARKET), Decimal("110"), 1700000001)

        services.save_portfolio(self.db_portfolio, portfolio)


    def test_untouched_chain_is_intact(self):
        self.assertEqual(
            services.verify_ledger(self.db_portfolio),
            {"intact": True, "entries": 2},
        )


    def test_edited_trade_is_caught(self):
        trade = self.db_portfolio.ledger_entries.get(sequence=0).trade
        trade.fill_price += Decimal("1")
        trade.save()

        result = services.verify_ledger(self.db_portfolio)

        self.assertFalse(result["intact"])
        self.assertEqual(result["sequence"], 0)
        self.assertEqual(result["failure"], "content")


    def test_deleted_entry_is_caught(self):
        self.db_portfolio.ledger_entries.get(sequence=0).delete()

        result = services.verify_ledger(self.db_portfolio)

        self.assertFalse(result["intact"])
        self.assertEqual(result["sequence"], 1)
        self.assertEqual(result["failure"], "link")
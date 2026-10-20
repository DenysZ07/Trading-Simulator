from django.test import TestCase
import json
from decimal import Decimal
from marketdata.models import Candle, Instrument
from marketdata.providers.shapes import Interval


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
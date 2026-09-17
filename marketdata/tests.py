from django.test import SimpleTestCase
from marketdata.providers.fake import FakeProvider
from marketdata.providers.shapes import Interval
from decimal import Decimal
from marketdata.providers.exceptions import SymbolNotFound
from marketdata.providers.alpaca import AlpacaProvider


class ProviderTests(SimpleTestCase):

    def get_provider(self):
        return FakeProvider()

    def get_symbol(self):
        return "TEST"

    def get_range(self):
        return 0, 0


    def test_candles_are_sorted(self):
        start, end = self.get_range()
        candles = self.get_provider().historical_candles(self.get_symbol(), Interval.DAY, start, end)

        timestamps = [c.timestamp for c in candles]
        self.assertEqual(timestamps, sorted(timestamps))


    def test_no_duplicate_timestamps(self):
        start, end = self.get_range()
        candles = self.get_provider().historical_candles(self.get_symbol(), Interval.DAY, start, end)

        timestamps = [c.timestamp for c in candles]
        self.assertEqual(len(timestamps), len(set(timestamps)))

    def test_prices_are_decimal(self):
        start, end = self.get_range()
        candles = self.get_provider().historical_candles(self.get_symbol(), Interval.DAY, start, end)

        for candle in candles: 
            self.assertIsInstance(candle.close, Decimal)

    def test_timestamps_are_int(self):
        start, end = self.get_range()
        candles = self.get_provider().historical_candles(self.get_symbol(), Interval.DAY, start, end)

        for candle in candles: 
            self.assertIsInstance(candle.timestamp, int)

    def test_unknown_symbol_raises(self):
        start, end = self.get_range()

        with self.assertRaises(SymbolNotFound): 
            self.get_provider().historical_candles("NOPE", Interval.DAY, start, end) 


class AlpacaTests(ProviderTests):

    def get_provider(self):
        return AlpacaProvider()

    def get_symbol(self):
        return "AAPL"

    def get_range(self):
        return 1786822500, 1789500900
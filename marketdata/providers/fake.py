from .base import MarketDataProvider
from .shapes import AssetClass, Candle, Instrument, Interval, Quote 
from decimal import Decimal
from .exceptions import SymbolNotFound


class FakeProvider(MarketDataProvider):


    def available_instruments(self) -> list[Instrument]:
        return [
            Instrument("TEST", "Test Instrument", AssetClass.EQUITY),   
        ]

        
    def historical_candles(self, symbol: str, interval: Interval, start: int, end: int) -> list[Candle]: 
        if symbol != "TEST":
            raise SymbolNotFound(symbol)

        return [
            Candle(1700000000, Decimal("100.00"), Decimal("105.00"), Decimal("99.00"), Decimal("104.00"), Decimal("1000")),
            Candle(1700086400, Decimal("104.00"), Decimal("108.00"), Decimal("103.00"), Decimal("107.00"), Decimal("1200")),
            Candle(1700172800, Decimal("107.00"), Decimal("107.50"), Decimal("101.00"), Decimal("102.00"), Decimal("900")),
        ]
        
    def latest_price(self, symbol: str) -> Quote:
        raise NotImplementedError
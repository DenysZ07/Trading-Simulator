from .base import MarketDataProvider
from .shapes import AssetClass, Candle, Instrument, Interval, Quote 



class FakeProvider(MarketDataProvider):


    def available_instruments(self) -> list[Instrument]:
        return [
            Instrument("TEST", "Test Instrument", AssetClass.EQUITY),   
        ]

        
    def historical_candles(self, symbol: str, interval: Interval, start: int, end: int) -> list[Candle]: 
        raise NotImplementedError
        

    
    def latest_price(self, symbol: str) -> Quote:
        raise NotImplementedError
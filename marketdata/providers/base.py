from abc import ABC, abstractmethod
from marketdata.providers.shapes import Instrument, Candle, Quote, Interval


class MarketDataProvider(ABC):
    @abstractmethod
    def available_instruments(self) -> list[Instrument]: 
        """Returns list of available instruments.
        Raises: ProviderUnavailable, RateLimited."""


    @abstractmethod
    def historical_candles(self, symbol: str, interval: Interval, start: int, end: int) -> list[Candle]: 
        """Returns list of historical candles. start and end are unix seconds. Pagination happens inside the provider.
        Raises: ProviderUnavailable, SymbolNotFound, RateLimited."""
        

    @abstractmethod
    def latest_price(self, symbol: str) -> Quote:
        """Returns the latest price for entered symbol.
        Raises: ProviderUnavailable, SymbolNotFound, RateLimited."""
import requests
from marketdata.providers.base import MarketDataProvider
from marketdata.providers.shapes import Candle, Quote, Interval, Instrument
import os


class AlpacaProvider(MarketDataProvider):

    ALPACA_URL = "https://data.alpaca.markets/v2"

    def __init__(self):
        self.api_id = os.environ["APCA_API_KEY_ID"]
        self.api_secret = os.environ["APCA_API_SECRET_KEY"]

    def available_instruments(self) -> list[Instrument]: 
        """Returns list of available instruments.
        Raises: ProviderUnavailable, RateLimited."""
        raise NotImplementedError
    

    def historical_candles(self, symbol: str, interval: Interval, start: int, end: int) -> list[Candle]: 
        """Returns list of historical candles. start and end are unix seconds. Pagination happens inside the provider.
        Raises: ProviderUnavailable, SymbolNotFound, RateLimited."""
        raise NotImplementedError
            
     
    def latest_price(self, symbol: str) -> Quote:
        """Returns the latest price for entered symbol.
        Raises: ProviderUnavailable, SymbolNotFound, RateLimited."""
        raise NotImplementedError
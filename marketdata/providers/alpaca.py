import requests
from marketdata.providers.base import MarketDataProvider
from marketdata.providers.shapes import Candle, Quote, Interval, Instrument, AssetClass
from marketdata.providers.exceptions import SymbolNotFound, ProviderUnavailable, RateLimited
import os
from datetime import timezone, datetime
import json
from decimal import Decimal


class AlpacaProvider(MarketDataProvider):

    ALPACA_URL = "https://data.alpaca.markets/v2"
    ALPACA_INTERVAL = {Interval.DAY: "1Day"}


    def __init__(self):
        self.api_id = os.environ["APCA_API_KEY_ID"]
        self.api_secret = os.environ["APCA_API_SECRET_KEY"]

    def available_instruments(self) -> list[Instrument]: 
        """Returns list of available instruments."""
        return [
            Instrument("AAPL", "Apple Inc.", AssetClass.EQUITY),
            Instrument("MSFT", "Microsoft Corporation", AssetClass.EQUITY),
            Instrument("NVDA", "NVIDIA Corporation", AssetClass.EQUITY),
            Instrument("JPM", "JPMorgan Chase & Co.", AssetClass.EQUITY),
            Instrument("GOOGL", "Alphabet Inc.", AssetClass.EQUITY),
        ]
    

    def historical_candles(self, symbol: str, interval: Interval, start: int, end: int) -> list[Candle]: 
        """Returns list of historical candles. start and end are unix seconds.
        Raises: ProviderUnavailable, SymbolNotFound, RateLimited."""


        headers = {"APCA-API-KEY-ID": self.api_id, "APCA-API-SECRET-KEY": self.api_secret}


        params = {"timeframe": self.ALPACA_INTERVAL[interval], 
                  "start": datetime.fromtimestamp(start, tz=timezone.utc).date().isoformat(), 
                  "end": datetime.fromtimestamp(end, tz=timezone.utc).date().isoformat(), 
                  "feed": "sip"}

        
        api_url = f"{self.ALPACA_URL}/stocks/{symbol}/bars"

        response = requests.get(url=api_url, params=params, headers=headers)

        if response.status_code == 404:
            raise SymbolNotFound(symbol)
        elif response.status_code == 429:
            raise RateLimited(symbol)
        elif response.status_code != 200:
            raise ProviderUnavailable(f"unexpected status {response.status_code}")
        
        data = json.loads(response.text, parse_float=Decimal)

        bars = data.get("bars")

        if not bars:
            raise SymbolNotFound(symbol)

        candles = []
        for bar in bars:
            candles.append(Candle(
                timestamp=int(datetime.fromisoformat(bar["t"]).timestamp()),
                open=bar["o"],
                high=bar["h"],
                low=bar["l"],
                close=bar["c"],
                volume=Decimal(bar["v"]),
            ))

        return candles
        
     
    def latest_price(self, symbol: str) -> Quote:
        """Returns the latest price for entered symbol.
        Raises: ProviderUnavailable, SymbolNotFound, RateLimited."""
        raise NotImplementedError


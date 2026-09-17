from django.core.management.base import BaseCommand
from datetime import datetime, timedelta, timezone

from marketdata.providers.alpaca import AlpacaProvider
from marketdata.providers.shapes import Interval
from marketdata.models import Candle, Instrument


class Command(BaseCommand):
    help = "Backfill historical candles from the provider"

    def handle(self, *args, **options):
        provider = AlpacaProvider()

        now = datetime.now(tz=timezone.utc)
        end = int((now - timedelta(days=1)).timestamp()) # Alpaca free tier rejects SIP data thats newer than 15 min (403) and todays daily bar wont be complete until close. 
        start = int((now - timedelta(days=730)).timestamp()) 

        for shape in provider.available_instruments():
            instrument, _ = Instrument.objects.get_or_create(
                symbol=shape.symbol,
                defaults={
                    "display_name": shape.display_name,
                    "asset_class": shape.asset_class.value,
                    "quote_currency": shape.quote_currency,
                }
            )

            candles = provider.historical_candles(shape.symbol, Interval.DAY, start, end)

            for candle in candles:
                Candle.objects.get_or_create(
                    instrument=instrument, 
                    interval=Interval.DAY.value,
                    timestamp=candle.timestamp,
                    defaults={
                        "open": candle.open,
                        "high": candle.high, 
                        "low": candle.low, 
                        "close": candle.close,
                        "volume": candle.volume,
                    }
                )



            self.stdout.write(f"{shape.symbol}: {len(candles)} candles")
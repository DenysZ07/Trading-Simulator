from django.core.management.base import BaseCommand

from marketdata.models import Instrument
from marketdata.providers.alpaca import AlpacaProvider


class Command(BaseCommand):
    help = "Backfill historical candles from the provider"

    def handle(self, *args, **options):
        provider = AlpacaProvider()

        for shape in provider.available_instruments():
            Instrument.objects.get_or_create(
                symbol=shape.symbol,
                defaults={
                    "display_name": shape.display_name,
                    "asset_class": shape.asset_class.value,
                    "quote_currency": shape.quote_currency,
                }
            )
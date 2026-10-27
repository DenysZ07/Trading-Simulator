from decimal import Decimal
from django.core.management.base import BaseCommand
from trading.models import LedgerEntry 

class Command(BaseCommand):
    help = "Changes one trade's fill price so that the ledger verification can be shown failing."

    def add_arguments(self, parser):
        parser.add_argument("sequence", type=int)

    def handle(self, *args, **options):
        entry = LedgerEntry.objects.filter(sequence=options["sequence"]).first()


        if entry is None: 
            self.stdout.write(f"No ledger entry with sequence {options['sequence']}")
            return

        trade = entry.trade
        trade.fill_price += Decimal("1")
        trade.save()


        self.stdout.write(f"Corrupted {trade.symbol} trade - the fill price is now {trade.fill_price}")
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Backfill historical candles from the provider"

    def handle(self, *args, **options):
        self.stdout.write("backfill starting")
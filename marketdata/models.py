from django.db import models


class Instrument(models.Model):


    class AssetClass(models.TextChoices):
        EQUITY = "equity", "Equity"


    symbol = models.CharField(max_length=6, unique=True)
    display_name = models.CharField(max_length=100)
    asset_class = models.CharField(max_length=20, choices=AssetClass.choices)
    quote_currency = models.CharField(max_length=3, default="USD")    


class Candle(models.Model):

    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    interval = models.CharField(max_length=10)
    timestamp = models.BigIntegerField()
    open = models.DecimalField(max_digits=20, decimal_places=8)
    high = models.DecimalField(max_digits=20, decimal_places=8)
    low = models.DecimalField(max_digits=20, decimal_places=8)
    close = models.DecimalField(max_digits=20, decimal_places=8)
    volume = models.DecimalField(max_digits=30, decimal_places=8)


    class Meta: 
        constraints = [
            models.UniqueConstraint(
                fields=["instrument", "interval", "timestamp"],
                name="unique_candle",
            )
        ]

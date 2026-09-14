from django.db import models


class Instrument(models.Model):


    class AssetClass(models.TextChoices):
        EQUITY = "equity", "Equity"


    symbol = models.CharField(max_length=6, unique=True)
    display_name = models.CharField(max_length=100)
    asset_class = models.CharField(max_length=20, choices=AssetClass.choices)
    quote_currency = models.CharField(max_length=3, default="USD")    

from django.db import models



class Portfolio(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    cash = models.DecimalField(max_digits=20, decimal_places=8)


class Position(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="positions")
    symbol = models.CharField(max_length=6)

    class Meta: 
        constraints = [
            models.UniqueConstraint(
                fields=["portfolio", "symbol"],
                name="unique_position",
            )
        ]


class Lot(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name="lots")
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=20, decimal_places=8)
    timestamp = models.BigIntegerField()


class Trade(models.Model):

    class Side(models.TextChoices):
        BUY = "buy", "Buy"
        SELL = "sell", "Sell"


    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="trades") 
    symbol = models.CharField(max_length=6)
    side = models.CharField(max_length=4, choices=Side.choices)
    quantity = models.IntegerField()
    fill_price = models.DecimalField(max_digits=20, decimal_places=8)
    commission = models.DecimalField(max_digits=20, decimal_places=8)
    slippage = models.DecimalField(max_digits=20, decimal_places=8)
    spread = models.DecimalField(max_digits=20, decimal_places=8)
    timestamp = models.BigIntegerField()
    cost_basis = models.DecimalField(max_digits=20, decimal_places=8, null=True)


class LedgerEntry(models.Model):

    """Rows are only ever added, never changed or deleted, and the code has no way to do either."""

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="ledger_entries")
    trade = models.OneToOneField(Trade, on_delete=models.PROTECT)
    sequence = models.PositiveIntegerField()
    payload = models.TextField()
    previous_digest = models.CharField(max_length=64)
    digest = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: 
        constraints = [
            models.UniqueConstraint(
                fields = ["portfolio", "sequence"],
                name = "unique_ledger_sequence"
            )
        ]

        ordering = ["sequence"]

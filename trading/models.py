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

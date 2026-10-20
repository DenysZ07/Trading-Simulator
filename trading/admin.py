from django.contrib import admin
from .models import Lot, Portfolio, Position, Trade

admin.site.register(Portfolio)
admin.site.register(Position)
admin.site.register(Lot)
admin.site.register(Trade)

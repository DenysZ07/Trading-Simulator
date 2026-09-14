from django.contrib import admin
from .models import Instrument, Candle

admin.site.register(Instrument)
admin.site.register(Candle)
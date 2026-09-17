from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from .models import Candle, Instrument
from .providers.shapes import Interval




def candles(request, symbol):
    instrument = get_object_or_404(Instrument, symbol=symbol.upper())

    rows = Candle.objects.filter(instrument=instrument, interval=Interval.DAY.value).order_by("timestamp")

    data = [
        {
            "time": row.timestamp,
            "open": float(row.open),
            "high": float(row.high),
            "low": float(row.low),
            "close": float(row.close)
        }
        for row in rows
    ]

    return JsonResponse(data, safe=False)
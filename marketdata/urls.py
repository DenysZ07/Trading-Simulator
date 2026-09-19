from django.urls import path
from . import views


urlpatterns = [path("api/candles/<str:symbol>/", views.candles, name="candles"),
               path("", views.demo, name="demo")]
from django.urls import path 
from . import views

urlpatterns = [
    path("api/order/", views.place_order, name="place_order"),
]
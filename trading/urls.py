from django.urls import path 
from . import views

urlpatterns = [
    path("api/order/", views.place_order, name="place_order"),
    path("api/portfolio/", views.portfolio_state, name="portfolio_state"),
    path("api/verify/", views.verify, name="verify"),
]
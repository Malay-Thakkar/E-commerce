from django.urls import path
from .views import *

urlpatterns = [
    path("cart/checkout/", checkout, name="checkout"),
    path("cart/shipping_address", shipping_address, name="shipping_address"),
    path("cart/checkout/placeorder", place_order, name="placeorder"),
]

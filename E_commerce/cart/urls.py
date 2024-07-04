from django.urls import path
from cart.views import cart_add,cart_delete,cart_summary,cart_update,wishlist_summary, wishlist_add, wishlist_delete

urlpatterns = [
    path('cart/',cart_summary,name="cart_summary"),
    path('cart/add/',cart_add,name="cart_add"),
    path('cart/delete/',cart_delete,name="cart_delete"), 
    path('cart/update/',cart_update,name="cart_update"),
    path('wishlist/', wishlist_summary, name="wishlist_summary"),
    path('wishlist/add/', wishlist_add, name="wishlist_add"),
    path('wishlist/delete/', wishlist_delete, name="wishlist_delete"),
]
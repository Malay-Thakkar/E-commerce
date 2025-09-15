from django.urls import path
from cart.views import cart_add,cart_delete,cart_summary,cart_update,wishlist_summary, wishlist_add, wishlist_delete,CartAddAPIView, WishlistAddAPIView, CartSummaryAPIView, CartDeleteAPIView, CartUpdateAPIView, ProductSearchAPIView

urlpatterns = [
    path('cart/',cart_summary,name="cart_summary"),
    path('cart/add/',cart_add,name="cart_add"),
    path('cart/delete/',cart_delete,name="cart_delete"), 
    path('cart/update/',cart_update,name="cart_update"),
    path('wishlist/', wishlist_summary, name="wishlist_summary"),
    path('wishlist/add/', wishlist_add, name="wishlist_add"),
    path('wishlist/delete/', wishlist_delete, name="wishlist_delete"),

    path('api/chatbot/cart/add/', CartAddAPIView.as_view(), name='api_chatbot_cart_add'),
    path('api/chatbot/wishlist/add/', WishlistAddAPIView.as_view(), name='api_chatbot_wishlist_add'),
    path('api/chatbot/cart/summary/', CartSummaryAPIView.as_view(), name='api_chatbot_cart_summary'),
    path('api/chatbot/cart/delete/', CartDeleteAPIView.as_view(), name='api_chatbot_cart_delete'),
    path('api/chatbot/cart/update/', CartUpdateAPIView.as_view(), name='api_chatbot_cart_update'),
    path('api/product/search/', ProductSearchAPIView.as_view(), name='api_product_search'),
]
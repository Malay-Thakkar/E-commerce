from cart.cart import Cart
from cart.wishlist import Wishlist

#get globally cart
def cart(request):
    return {'cart':Cart(request)}

#get globally wishlist
def wishlist(request):
    return {'wishlist':Wishlist(request)}
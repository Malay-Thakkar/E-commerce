from django.shortcuts import render, get_object_or_404
from api.models import ProductModel
from django.http import JsonResponse
from .cart import Cart
from .wishlist import Wishlist
from django.contrib import messages

# Create your views here.

#cart page view 
def cart_summary(request):
    cart=Cart(request)
    cart_products =cart.get_cart_product()
    cart_quantity =cart.get_quantity()
    total = cart.cart_total()
    gsttotal = cart.cart_gsttotal()
    return render(request,'cart.html',{'cart_products':cart_products,'cart_quantity':cart_quantity,'total':total,'gsttotal':gsttotal})


#for add products in carts 
def cart_add(request):
    cart = Cart(request)
    if request.POST.get('action')=='post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        #get from DB
        product = get_object_or_404(ProductModel,product_id=product_id)
        cart.add(product=product,quantity=product_qty)
        cart_quantity = len(cart)
        # cart_quantity = cart.__len__()
        response =JsonResponse({'cart_quantity':cart_quantity})
        messages.success(request,'successfully added Items')
        return response
    
#for delete products in cart
def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action')=='post':
        product_id = int(request.POST.get('product_id'))
        cart.delete(product=product_id)
        response = JsonResponse({'product_id':product_id})
        messages.success(request,'successfully deleted Items')
        return response

#for update products(quantity) in cart
def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action')=='post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        cart.update(product=product_id,quantity=product_qty)
        response = JsonResponse({'qty':product_qty})
        return response

#wishlist views:
def wishlist_summary(request):
    wishlist = Wishlist(request)
    wishlist_products = wishlist.get_wishlist_product()
    return render(request, 'wishlist.html', {'wishlist_products': wishlist_products})

#for add product in wishlist
def wishlist_add(request):
    wishlist = Wishlist(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product = get_object_or_404(ProductModel, product_id=product_id)
        wishlist.add(product=product)
        messages.success(request, 'Successfully added to wishlist')
        return JsonResponse({'success': True})

#for delete product in wishlist
def wishlist_delete(request):
    wishlist = Wishlist(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        wishlist.delete(product_id)
        messages.success(request, 'Successfully deleted from wishlist')
        return JsonResponse({'success': True})

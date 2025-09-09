from django.shortcuts import render, get_object_or_404
from api.models import ProductModel
from django.http import JsonResponse
from .cart import Cart
from .wishlist import Wishlist
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .serializers import (
    CartWishlistSerializer, 
    CartUpdateSerializer,
)
from api.serializers import(
    ProductSerializers,
    CategorySerializers
)
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


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

#for rasa handel apis
class CartAddAPIView(APIView):
    """API endpoint for the chatbot to add items to the user's cart."""
    permission_classes = [IsAuthenticated]
    print("\n\n\n\n\n\n\tsfdfsdfsdf CartAddAPIView")
    def post(self, request, *args, **kwargs):
        serializer = CartWishlistSerializer(data=request.data)
        print("\n\n\n\n\n\n\tsfdfsdfsdf",request.data)
        if serializer.is_valid():
            cart = Cart(request)
            print("\n\n\n\n\n\n\tcccccccccccfsdf",cart)
            product_id = serializer.validated_data['product_id']
            print("\n\n\n\n\n\n\tsfdfsdfsdf",product_id)
            try:
                product = ProductModel.objects.get(product_id=product_id)
                print("\n\n\n\n\nlllllllllllllllllllldf",product)
                cart.add(product=product, quantity=1)
                print("\n\n\n\n\n\n\tsfdfsdfsdf",cart)
                return Response(
                    {"status": "success", "message": f"{product.name} added to cart."},
                    status=status.HTTP_200_OK
                )
            except ProductModel.DoesNotExist:
                return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WishlistAddAPIView(APIView):
    """API endpoint for the chatbot to add items to the user's wishlist."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CartWishlistSerializer(data=request.data)
        if serializer.is_valid():
            wishlist = Wishlist(request)
            product_id = serializer.validated_data['product_id']

            try:
                product = ProductModel.objects.get(product_id=product_id)
                wishlist.add(product=product)
                return Response(
                    {"status": "success", "message": f"{product.name} added to wishlist."},
                    status=status.HTTP_200_OK
                )
            except ProductModel.DoesNotExist:
                return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartSummaryAPIView(APIView):
    """API endpoint for the chatbot to view the user's cart."""
    print("\n\n\n\n\n\n\tsfdfsdfsdf CartSummaryAPIView")

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        cart_products = cart.get_cart_product() # This likely returns product objects
        
        # We need to serialize the product data to send it as JSON
        products_data = [
            {
                'name': item['product'].name,
                'quantity': item['quantity'],
                'price': item['price']
            }
            for item in cart_products
        ]

        response_data = {
            'products': products_data,
            'total': cart.cart_total(),
            'gst_total': cart.cart_gsttotal()
        }
        return Response(response_data, status=status.HTTP_200_OK)

class CartDeleteAPIView(APIView):
    """API endpoint for the chatbot to delete items from the user's cart."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CartWishlistSerializer(data=request.data)
        if serializer.is_valid():
            cart = Cart(request)
            product_id = serializer.validated_data['product_id']
            # Your cart.delete method expects an integer product_id
            cart.delete(product=product_id)
            return Response(
                {"status": "success", "message": "Item removed from cart."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartUpdateAPIView(APIView):
    """API endpoint for the chatbot to update item quantities in the cart."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CartUpdateSerializer(data=request.data)
        if serializer.is_valid():
            cart = Cart(request)
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            # Your cart.update method expects integer product_id and quantity
            cart.update(product=product_id, quantity=quantity)
            return Response(
                {"status": "success", "message": "Cart updated."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.shortcuts import render, redirect, get_object_or_404
from cart.cart import Cart
from payment.models import Order, OrderItems, Payment, ShippingAddressModel
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# Create your views here.
@login_required(login_url="/signin")
# customer chackout page
def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_cart_product()
    cart_quantity = cart.get_quantity()
    total = cart.cart_total()
    gsttotal = cart.cart_gsttotal()
    address = ShippingAddressModel.objects.filter(user=request.user)
    return render(
        request,
        "checkout.html",
        {
            "cart_products": cart_products,
            "cart_quantity": cart_quantity,
            "total": total,
            "gsttotal": gsttotal,
            "address": address,
        },
    )


# customer add shipping address
def shipping_address(request):
    cart = Cart(request)
    cart_products = cart.get_cart_product()
    cart_quantity = cart.get_quantity()
    total = cart.cart_total()
    gsttotal = cart.cart_gsttotal()
    address = ShippingAddressModel.objects.filter(user=request.user)

    if request.method == "POST":
        # Retrieve shipping address data from the form
        shipping_first_name = request.POST.get("shipping_first_name")
        shipping_last_name = request.POST.get("shipping_last_name")
        shipping_phone = request.POST.get("shipping_phone")
        shipping_email = request.POST.get("shipping_email")
        shipping_address = request.POST.get("shipping_address")
        shipping_city = request.POST.get("shipping_city")
        shipping_state = request.POST.get("shipping_state")
        shipping_note = request.POST.get("shipping_note")

        # Create a new ShippingAddressModel instance
        shipping_address = ShippingAddressModel.objects.create(
            user=request.user,
            shipping_first_name=shipping_first_name,
            shipping_last_name=shipping_last_name,
            shipping_phone=shipping_phone,
            shipping_email=shipping_email,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_state=shipping_state,
            shipping_note=shipping_note,
        )
        return render(
            request,
            "checkout.html",
            {
                "cart_products": cart_products,
                "cart_quantity": cart_quantity,
                "total": total,
                "gsttotal": gsttotal,
                "address": address,
            },
        )


# customer place order request
@login_required(login_url="/signin")
def place_order(request):
    if request.method == "POST":

        # Retrieve payment method from the request POST data
        payment_method = request.POST.get("payment_method")
        order_note = request.POST.get("ordernote")
        Full_name = request.POST.get("Full_name")
        address_id = request.POST.get("shipping_address")

        # validate shipping address
        if not address_id:
            messages.error(request, "Please add shipping address.")
            return redirect("checkout")
        else:
            try:
                shipping_address = ShippingAddressModel.objects.get(id=address_id)
            except ShippingAddressModel.DoesNotExist:
                messages.error(request, "The selected shipping address does not exist.")
                return redirect("checkout")

        # Validate payment method
        if not payment_method:
            messages.error(request, "Please select a payment method.")
            return redirect("checkout")

        # Retrieve user's cart items
        cart = Cart(request)
        cart_products = cart.get_cart_product()
        cart_quantity = cart.get_quantity()
        order_total_gst = cart.cart_gsttotal()
        order_total = cart.cart_total()

        # Create a new Payment instance
        payment = Payment.objects.create(
            user=request.user,
            payment_method=payment_method,
            amount_paid=order_total,
            status="Not_Completed",
        )

        # Create a new Order instance
        order = Order.objects.create(
            user=request.user,
            payment=payment,
            full_name=Full_name,
            shipping_address=shipping_address,
            order_total=order_total,
            order_total_gst=order_total_gst,
            order_note=order_note,
        )

        # Create OrderItems instances and link them to the order
        for product in cart_products:
            OrderItems.objects.create(
                Order=order,
                product=product,
                img=product.img,
                name=product.name,
                user=request.user,
                quantity=cart_quantity[str(product.product_id)],
                price=product.price,
                total_price=product.price * cart_quantity[str(product.product_id)],
            )

        # Clear the user's cart
        cart.delete_all()

        messages.success(request, "Your order has been placed successfully!")
        return redirect("/order")

    else:
        messages.error(
            request, "Please correct the errors in the shipping address form."
        )
        return redirect("checkout")

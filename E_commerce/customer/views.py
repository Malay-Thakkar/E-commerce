from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from E_commerce.settings import EMAIL_BACKEND, EMAIL_HOST_USER
from customer.models import CustomUser
from api.models import ProductModel
from payment.models import Order, OrderItems, Payment
from cart.cart import Cart
from cart.wishlist import Wishlist
import json

# Create your views here.
User = get_user_model()


# register user
def signup(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")
        Address = request.POST.get("Address")
        tandc = request.POST.get("tandc")

        if (
            not first_name
            or not last_name
            or not username
            or not email
            or not password
            or not phone
            or not Address
        ):
            messages.error(request, "All fields are required!")
            return redirect("/signup/")

        user = User.objects.filter(username=username)
        if user.exists():
            messages.info(request, "Username already taken!")
            return redirect("/signup/")

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            phone=phone,
            Address=Address,
            tandc=tandc,
        )
        user.set_password(password)
        user.save()

        messages.info(request, "Account created Successfully!")
        return redirect("/signin/")
    return render(request, "signup.html")


# for login
def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not User.objects.filter(username=username).exists():
            messages.error(request, "Invalid Username")
            return redirect("/signin/")
        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, "Invalid Password")
            return redirect("/signin/")
        else:
            login(request, user)
            current_user = CustomUser.objects.get(id=request.user.id)
            saved_cart = current_user.old_cart
            saved_wishlist = current_user.old_wishlist
            if saved_cart:
                converted_cart = json.loads(saved_cart)
                cart = Cart(request)
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            if saved_wishlist:
                converted_wishlist = json.loads(saved_wishlist)
                wishlist = Wishlist(request)
                for key, value in converted_wishlist.items():
                    wishlist.db_add_wishlist(product=key)
            return redirect("/")
    return render(request, "signin.html")


def signout(request):
    logout(request)
    return redirect("/signin")


def home(request):
    return render(request, "index.html")


def product(request):
    return render(request, "products.html")


def productdetail(request, productid):
    return render(request, "productdetail.html", {"productid": productid})


def productfilter(request, categoryid):
    return render(request, "productfilter.html", {"categoryid": categoryid})


def tandc(request):
    return render(request, "tandc.html")


def notfound(request):
    return render(request, "404.html")


def thankyou(request):
    return render(request, "thankyou.html")


def aboutus(request):
    return render(request, "aboutus.html")


# contactus page and send mail
def contactus(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        email = request.POST.get("email")
        query = request.POST.get("query")
        subject = "Website query"
        message = [name, phone, address, email, query]
        message_string = "\n".join(message)
        sender_email = settings.EMAIL_HOST_USER
        recipient_list = ["malay.thakkar@drcsystems.com", email]
        send_mail(subject, message_string, sender_email, recipient_list)
        # messages.success(request,"Thank you for connecting us")
        return render(request, "thankyou.html")
    return render(request, "contactus.html")


# search products
def search(request):
    if request.method == "POST":
        searched = request.POST.get("search")
        # qury for search product in database
        searched = ProductModel.objects.filter(name__icontains=searched)
        if not searched:
            messages.error(request, "no product found try other!!!")
            return render(request, "search.html", {})
        else:
            return render(request, "search.html", {"search": searched})
    return render(request, "search.html")


# profile page
@login_required(login_url="/signin")
def profile(request):
    logged_in_user = request.user
    myuser = CustomUser.objects.filter(username=logged_in_user).values()
    context = {"myuser": myuser}
    return render(request, "profile.html", context)


# update users data
@login_required(login_url="/signin")
def updateuser(request):
    logged_in_user = request.user
    myuser = CustomUser.objects.get(username=logged_in_user)
    context = {"myuser": myuser}
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        Address = request.POST.get("Address")

        if (
            not first_name
            or not last_name
            or not username
            or not email
            or not phone
            or not Address
        ):
            messages.error(request, "All fields are required!")
            return redirect("/profile/")

        # check username is exits or not?
        if (
            username != myuser.username
            and CustomUser.objects.filter(username=username).exists()
        ):
            messages.error(request, "Username already taken!")
            return redirect("/updateuser/")

        # Update user object with new values
        myuser.first_name = first_name
        myuser.last_name = last_name
        myuser.username = username
        myuser.email = email
        myuser.phone = phone
        myuser.Address = Address

        myuser.save()

        messages.info(request, "Profile Updated Successfully!")
        return redirect("/profile/")

    return render(request, "updateuser.html", context)


# for change passwoard
@login_required(login_url="/signin")
def changepasswd(request):
    logged_in_user = request.user
    myuser = CustomUser.objects.get(username=logged_in_user)
    if request.method == "POST":
        oldpasswd = request.POST.get("oldpasswd")
        newpasswd = request.POST.get("newpasswd")
        conformpasswd = request.POST.get("conformpasswd")

        if conformpasswd == newpasswd:
            user = authenticate(username=myuser.username, password=oldpasswd)
            if user is None:
                messages.error(request, "Invalid old Password")
                return redirect("/changepasswd/")
            else:
                myuser.set_password(conformpasswd)
                myuser.save()
                messages.success(request, "successfully chang Password")
                return redirect("/signin/")

        else:
            messages.error(request, "conformpasswd and newpasswd are not same!!!")
    return render(request, "updatepasswd.html")


# for forgate passwoard
def forgotpasswd(request):
    pass


# for permenent delete account/user
@login_required(login_url="/signin")
def deleteuser(request):
    logged_in_user = request.user
    myuser = CustomUser.objects.get(username=logged_in_user)
    myuser.delete()
    messages.error(request, "Your account is successfully deleted !!!")
    return redirect("/signup/")


# display users order
@login_required(login_url="/signin")
def order(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "order.html", {"orders": orders})


# display user order details
@login_required(login_url="/signin")
def orderdetail(request, orderid):
    order = Order.objects.get(id=orderid)
    # payment = Payment.objects.get(id=orderid)
    order_products = OrderItems.objects.filter(Order=orderid)
    if order.user == request.user:
        return render(
            request,
            "orderdetail.html",
            {"order": order, "order_products": order_products},
        )
    elif not order:
        return render(request, "orderdetail.html")
    else:
        return render(
            request, "404.html", {"error": "You are not authorized to access that!"}
        )


# for cancel order if order is not placed
@login_required(login_url="/signin")
def cancelorder(request, orderid):
    cancel_order_obj = Order.objects.get(id=orderid)
    orders = Order.objects.filter(user=request.user)
    if cancel_order_obj.user == request.user:
        if cancel_order_obj.order_status == "Pending":
            cancel_order_obj.delete()
            messages.success(request, "You order is canceled")
            return redirect("/order/")
        else:
            messages.error(request, "You can not cancelorder!!! order is placed")
            return redirect("/order/")
    else:
        messages.error(request, "You are not authorized!!!")
        return redirect("/order/")

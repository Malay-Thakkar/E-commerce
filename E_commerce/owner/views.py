from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from api.models import ProductModel, CategoryModel
from payment.models import Order, OrderItems, Payment
from payment.models import Order, OrderItems
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.db.models import Sum, F, ExpressionWrapper, FloatField, Q
from django.db import connection
import json
from customer.views import order

# Create your views here.

CustomUser = get_user_model()


# ================================ dashboard ============================
# custom admin dashboard
@login_required(login_url="/signin")
def dashboard(request):
    if request.user.is_staff:
        product_total = ProductModel.objects.count()
        category_total = CategoryModel.objects.count()
        order_total = Order.objects.count()
        user_total = CustomUser.objects.count()
        sale_total = Order.objects.aggregate(total_sale=Sum("order_total"))[
            "total_sale"
        ]
        stock_total = ProductModel.objects.annotate(
            total_price=ExpressionWrapper(
                F("price") * F("stock"), output_field=FloatField()
            )
        ).aggregate(total_stock_price=Sum("total_price"))["total_stock_price"]

        context = {
            "product_total": product_total,
            "category_total": category_total,
            "order_total": order_total,
            "user_total": user_total,
            "stock_total": stock_total,
            "sale_total": sale_total,
        }
        return render(request, "dashboard.html", context)
    return redirect("/")


# ================================ order ============================
# custom admin order page
@login_required(login_url="/signin")
def adminorder(request):
    if request.user.is_staff:
        orders = Order.objects.all()
        payment = Payment.objects.all()
        return render(
            request, "adminorder.html", {"orders": orders, "payment": payment}
        )
    return redirect("/")


# custom admin order-detail page
@login_required(login_url="/signin")
def adminorderdetail(request, order_id):
    if request.user.is_staff:
        try:
            order = Order.objects.get(id=order_id)
            # payment = Payment.objects.get(id=orderid)
            order_products = OrderItems.objects.filter(Order=order_id)
            if order:
                return render(
                    request,
                    "adminorderdetails.html",
                    {"order": order, "order_products": order_products},
                )
            else:
                return render(request, "404.html", {"error": "order not found"})
        except Order.DoesNotExist:
            return render(request, "404.html", {"error": "Order not found"})
    return redirect("/")


# custom admin order add page
@login_required(login_url="/signin")
def adminorderadd(request):
    if request.user.is_staff:
        if request.method == "POST":

            products_data = request.POST.get("productsObject")
            products_dict = json.loads(
                products_data
            )  # Convert the JSON string to a Python dictionary

            # calculate total price
            total = 0
            for key, value in products_dict.items():
                key = int(key)
                prod = ProductModel.objects.filter(product_id=key).values().first()
                if prod is not None:
                    total += prod["price"] * value
                else:
                    print(f"Product with ID {key} not found.")

            full_name = request.POST.get("fullname")
            payment_method = request.POST.get("payment_method")
            payment_status = request.POST.get("payment_status")
            order_status = request.POST.get("order_status")
            order_total = total
            order_total_gst = ((total * 18) / 100) + total
            order_note = request.POST.get("order_note")

            # Validate form data
            if not (
                full_name
                and payment_method
                and payment_status
                and order_total
                and order_status
            ):
                messages.error(request, "Please fill required all fields.")
                return redirect("adminorderadd")

            # Create a new Payment instance
            payment = Payment.objects.create(
                user=request.user,
                payment_method=payment_method,
                amount_paid=order_total,
                status=payment_status,
            )
            # Create a new Order instance
            order = Order.objects.create(
                user=request.user,
                payment=payment,
                full_name=full_name,
                order_total=order_total,
                order_total_gst=order_total_gst,
                order_status=order_status,
                order_note=order_note,
            )
            for id, quantity in products_dict.items():
                product_id = id
                quantity = quantity
                # Get the product based on the ID
                product = ProductModel.objects.get(product_id=product_id)
                # Create OrderItems instance
                OrderItems.objects.create(
                    Order=order,
                    product=product,
                    img=product.img,
                    name=product.name,
                    user=request.user,
                    quantity=quantity,
                    price=product.price,
                    total_price=product.price * quantity,
                )

            messages.success(request, "Order has been added successfully!")
            return redirect("adminorder")
        products = ProductModel.objects.all()
        return render(request, "adminaddorder.html", {"products": products})
    return redirect("/")


# for custom admin order update page render
@login_required(login_url="/signin")
def adminorderupdate(request, order_id):
    if request.user.is_staff:
        try:
            order = Order.objects.get(id=order_id)
            payment = order.payment
            order_products = OrderItems.objects.filter(Order=order_id)
            products = ProductModel.objects.all()
            if order:
                return render(
                    request,
                    "adminupdateorder.html",
                    {
                        "order": order,
                        "order_products": order_products,
                        "payment": payment,
                        "products": products,
                    },
                )
            else:
                return render(request, "404.html", {"error": "Order not found"})
        except Order.DoesNotExist:
            return render(request, "404.html", {"error": "Order not found"})

    return redirect("/")


# custom admin orderupdate post request
@login_required(login_url="/signin")
def adminorderdetailupdate(request, order_id, payment_id):
    if request.user.is_staff:
        if request.method == "POST":
            products_data = request.POST.get("productsObject")
            products_dict = json.loads(products_data)

            # Calculate total price
            total = 0.0
            for key, value in products_dict.items():
                key = int(key)
                prod = ProductModel.objects.filter(product_id=key).first()
                if prod is not None:
                    total += float(prod.price) * float(value)
                else:
                    print(f"Product with ID {key} not found.")

            full_name = request.POST.get("fullname")
            payment_method = request.POST.get("payment_method")
            payment_status = request.POST.get("payment_status")
            order_status = request.POST.get("order_status")
            order_note = request.POST.get("order_note")

            # Validate form data
            if not (full_name and payment_method and payment_status and order_status):
                messages.error(request, "Please fill all required fields.")
                return redirect("adminorderadd")

            # Payment updates
            payment_obj = get_object_or_404(Payment, id=payment_id)
            payment_obj.payment_method = payment_method
            payment_obj.amount_paid = total
            payment_obj.status = payment_status
            payment_obj.save()

            # Order Update
            order_obj = get_object_or_404(Order, id=order_id)
            order_obj.full_name = full_name
            order_obj.order_total = total
            order_obj.order_total_gst = ((total * 18) / 100) + total
            order_obj.order_status = order_status
            order_obj.order_note = order_note
            order_obj.save()

            # shipping address update
            # shipping_add_obj = get_object_or_404(ShippingAddressModel, id=shipping_add_id)
            # print(shipping_add_obj)

            # orderitem Update
            # OrderItem Update
            for order_item in order_obj.orderitems_set.all():
                product_id = order_item.product.product_id
                quantity_str = products_dict.get(
                    str(product_id), "0"
                )  # Get quantity from updated products data
                quantity = int(quantity_str)  # Convert quantity to integer
                if quantity > 0:
                    # Update existing order item
                    order_item.quantity = quantity
                    order_item.total_price = order_item.price * quantity
                    order_item.save()
                else:
                    # Delete order item if not present in updated products
                    order_item.delete()

            # Add new order items for products not present in existing order
            existing_product_ids = set(
                order_obj.orderitems_set.values_list("product__product_id", flat=True)
            )
            for product_id, quantity in products_dict.items():
                product_id = int(product_id)
                if product_id not in existing_product_ids and quantity > 0:
                    product = ProductModel.objects.filter(product_id=product_id).first()
                    if product:
                        OrderItems.objects.create(
                            Order=order_obj,
                            product=product,
                            img=product.img,
                            name=product.name,
                            user=request.user,
                            quantity=int(quantity),
                            price=product.price,
                            total_price=product.price * int(quantity),
                        )

            messages.success(request, "Order updated successfully.")
            return redirect("/admin/order/")
        try:
            order = Order.objects.get(id=order_id)
            payment = order.payment  # Assuming order.payment returns a Payment object
            order_products = OrderItems.objects.filter(Order=order_id)
            if order:
                return render(
                    request,
                    "adminupdateorder.html",
                    {
                        "order": order,
                        "order_products": order_products,
                        "payment": payment,
                    },
                )
            else:
                return render(request, "404.html", {"error": "Order not found"})
        except Order.DoesNotExist:
            return render(request, "404.html", {"error": "Order not found"})

    return redirect("/")


# custom admin order delete post request
@login_required(login_url="/signin")
def adminorderdetaildelete(request, order_id):
    if request.user.is_staff:
        if request.method == "POST":
            order = Order.objects.get(id=order_id)
            order.delete()
            return redirect("/admin/order")
    return redirect("/")


# custom admin search order live(ajex)
@login_required(login_url="/signin")
def searchorder(request):
    if request.method == "GET":
        query = request.GET.get("search")
        if query:
            results = Order.objects.filter(Q(user__username__icontains=query))
            context = {"orders": results}
            html_content = render(request, "search_order.html", context).content.decode(
                "utf-8"
            )
            return JsonResponse({"html": html_content})
    return JsonResponse({"html": ""})


# ================================ user ============================
# custom admin user page
@login_required(login_url="/signin")
def adminuser(request):
    if request.user.is_staff:
        users = CustomUser.objects.all()
        return render(request, "adminuser.html", {"users": users})
    return redirect("/")


# custom admin user-detail page
@login_required(login_url="/signin")
def adminuserdetail(request, user_id):
    if request.user.is_staff:
        user = CustomUser.objects.get(id=user_id)
        return render(request, "adminuserdetails.html", {"user": user})
    return redirect("/")


# custom admin user-add page
@login_required(login_url="/signin")
def adminuseradd(request):
    if request.user.is_staff:
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

            user = CustomUser.objects.filter(username=username)
            if user.exists():
                messages.info(request, "Username already taken!")
                return redirect("/signup/")
            user = CustomUser.objects.create_user(
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
            return redirect("/admin/users/")

    return redirect("/")


# custom admin user-update page
@login_required(login_url="/signin")
def adminuserdetailupdate(request, user_id):
    if request.user.is_staff:
        myuser = CustomUser.objects.get(id=user_id)
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
                return redirect("/admin/users/")
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
            return redirect("/admin/users/")
        return render(request, "updateuser.html", context)
    return redirect("/")


# custom admin user-delete page
@login_required(login_url="/signin")
def adminuserdelete(request, user_id):
    if request.user.is_staff:
        user = CustomUser.objects.get(id=user_id)
        if request.method == "POST":
            user.delete()
            messages.error(request, "{user_id}-account is successfully deleted !!!")
            return render(request, "adminuserdetails.html", {"user": user})
        else:
            return render(request, "adminuserdetails.html", {"user": user})
    return redirect("/")


# ================================ category ============================
# custom admin category page
@login_required(login_url="/signin")
def admincategory(request):
    if request.user.is_staff:
        categorys = CategoryModel.objects.all()
        return render(request, "admincategory.html", {"Categorys": categorys})
    return redirect("/")


# custom admin category-add
@login_required(login_url="/signin")
def admincategoryadd(request):
    if request.user.is_staff:
        if request.method == "POST":
            category = request.POST.get("category")
            if CategoryModel.objects.filter(category=category).exists():
                messages.error(request, f"A {category}' already exists!")
                return redirect("/admin/products/")
            if not category:
                messages.error(request, "All fields are required!")
            newcategory = CategoryModel(category=category)
            newcategory.save()
            messages.success(request, "category added successfully!!!")
            return redirect("/admin/category/")
    return redirect("/")


# custom admin category-update
@login_required(login_url="/signin")
def admincategoryupdate(request, category_id):
    if request.user.is_staff:
        if request.method == "POST":
            category_obj = CategoryModel.objects.get(category_id=category_id)
            if category_obj:
                new_category_name = request.POST.get("category")
                if not new_category_name:
                    messages.error(request, "All fields are required!")
                    return redirect("/admin/category/")
                else:
                    category_obj.category = new_category_name
                    category_obj.save()
                    messages.success(request, "Category updated successfully!!!")
                    return redirect("/admin/category/")
            else:
                return render(request, "404.html", {"error": "Category not found"})
    return redirect("/")


# custom admin category-delete
@login_required(login_url="/signin")
def admincategorydelete(request, category_id):
    if request.user.is_staff:
        if request.method == "POST":
            category = CategoryModel.objects.get(category_id=category_id)
            if category:
                category.delete()
                messages.error(request, "category deleted successfully!!!")
                return redirect("/admin/category/")
            else:
                return render(request, "404.html", {"error": "category not found"})
    return redirect("/")


# ================================ product ============================
# custom admin Product page
@login_required(login_url="/signin")
def adminproducts(request):
    if request.user.is_staff:
        domain = request.get_host()
        products = ProductModel.objects.all()
        categorys = CategoryModel.objects.all()
        return render(
            request,
            "adminproduts.html",
            {"products": products, "categorys": categorys, "domain": domain},
        )
    return redirect("/")


# custom admin Product-add
@login_required(login_url="/signin")
def adminproductadd(request):
    if request.user.is_staff:
        if request.method == "POST":
            name = request.POST.get("name")
            price = request.POST.get("price")
            unit = request.POST.get("unit")
            stock = request.POST.get("stock")
            img = request.FILES.get("img")
            desc = request.POST.get("desc")
            category_id = request.POST.get("category")

            # Move the print statement after the category variable is assigned
            category = get_object_or_404(CategoryModel, pk=category_id)

            # Check if a product with the same name already exists
            if ProductModel.objects.filter(name=name).exists():
                messages.error(
                    request, f"A product with the name '{name}' already exists!"
                )
                return redirect("/admin/products/")

            if (
                not name
                or not price
                or not unit
                or not stock
                or not img
                or not desc
                or not category
            ):
                messages.error(request, "All fields are required!")
                return redirect("/admin/products/")

            newproduct = ProductModel(
                name=name,
                price=price,
                unit=unit,
                stock=stock,
                img=img,
                desc=desc,
                category=category,
            )
            newproduct.save()
            messages.success(request, "product added successfully!!!")
            return redirect("/admin/products/")
        return redirect("/")


# custom admin Product-update
@login_required(login_url="/signin")
def adminproductsupdate(request, product_id):
    if request.user.is_staff:
        if request.method == "POST":
            product = ProductModel.objects.get(product_id=product_id)
            if product:
                name = request.POST.get("name")
                price = request.POST.get("price")
                unit = request.POST.get("unit")
                stock = request.POST.get("stock")
                img = request.FILES.get("img")
                desc = request.POST.get("desc")
                category_id = request.POST.get("category")

                # Move the print statement after the category variable is assigned
                category = get_object_or_404(CategoryModel, pk=category_id)

                if (
                    not name
                    or not price
                    or not unit
                    or not stock
                    or not img
                    or not desc
                    or not category
                ):
                    messages.error(request, "All fields are required!")
                    return redirect("/admin/products/")

                product.name = name
                product.price = price
                product.unit = unit
                product.stock = stock
                product.img = img
                product.desc = desc
                product.category = category
                product.save()
                messages.success(request, "product updated successfully!!!")
                return redirect("/admin/products/")
            else:
                messages.error(request, "product not found")
                return render(request, "404.html", {"error": "Product ID not found"})
    return redirect("/")


# custom admin Product-delete
@login_required(login_url="/signin")
def adminproductsdelete(request, product_id):
    if request.user.is_staff:
        if request.method == "POST":
            product = ProductModel.objects.get(product_id=product_id)
            if product:
                product.delete()
                messages.error(request, "product deleted successfully!!!")
                return redirect("/admin/products/")
            else:
                return render(request, "404.html", {"error": "product id not found"})
    return redirect("/")


# custom admin Product-live search(ajex request)
@login_required(login_url="/signin")
def searchproduct(request):
    if request.method == "GET":
        query = request.GET.get("search")
        if query:
            results = ProductModel.objects.filter(
                Q(name__icontains=query) | Q(category__category__icontains=query)
            )
            context = {"products": results}
            return JsonResponse(
                {
                    "html": render(
                        request, "search_products.html", context
                    ).content.decode("utf-8")
                }
            )
    return JsonResponse({"html": ""})


# custom admin Category-live search(ajex request)
@login_required(login_url="/signin")
def searchcategory(request):
    if request.method == "GET":
        query = request.GET.get("search")
        if query:
            results = CategoryModel.objects.filter(Q(category__icontains=query))
            context = {"Categorys": results}
            return JsonResponse(
                {
                    "html": render(
                        request, "search_category.html", context
                    ).content.decode("utf-8")
                }
            )
    return JsonResponse({"html": ""})


# =====================================truncate ===========================
def truncate_table(request):
    if request.method == "POST":
        table_name = request.POST.get("table_name")
        with connection.cursor() as cursor:
            cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
        messages.success(request, f"{table_name} reset successfully!!!")
        return redirect("/admin/settings/")


# setting page
def settings(request):
    tables = [
        "api_productmodel",
        "api_categorymodel",
        "payment_order",
        "payment_orderitems",
        "payment_payment",
        "payment_shippingaddressmodel",
    ]
    context = {"table_names": tables}
    return render(request, "admin_settings.html", context)

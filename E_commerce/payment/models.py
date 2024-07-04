from django.db import models
from django.conf import settings
from api.models import ProductModel

# Create your models here.


# payment
class Payment(models.Model):
    STATUS = (
        ("Completed", "Completed"),
        ("Not_Completed", "Not_Completed"),
    )
    method = (("cash", "cash"), ("online", "online"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment_method = models.CharField(choices=method)
    amount_paid = models.CharField(max_length=100)  # this is the total amount paid
    status = models.CharField(choices=STATUS, default="Not_Completed")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


# shipping address model
class ShippingAddressModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    shipping_first_name = models.CharField(max_length=50)
    shipping_last_name = models.CharField(max_length=50)
    shipping_phone = models.CharField(max_length=12)
    shipping_email = models.EmailField(max_length=50)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=50)
    shipping_state = models.CharField(max_length=50)
    shipping_note = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.shipping_first_name} {self.shipping_last_name} {self.shipping_address} {self.shipping_city} {self.shipping_phone} {self.shipping_email} user:{self.user}"

    class Meta:
        verbose_name = "Shipping Address"
        verbose_name_plural = "Shipping Address"


# Order model
class Order(models.Model):
    STATUS = (
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
    shipping_address = models.ForeignKey(
        ShippingAddressModel, on_delete=models.CASCADE, blank=True, null=True
    )
    full_name = models.CharField(max_length=250)
    order_status = models.CharField(choices=STATUS, default="Pending")
    order_note = models.CharField(max_length=50, blank=True, null=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    order_total_gst = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


# Order Items model


class OrderItems(models.Model):
    Order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(ProductModel, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    img = models.FileField(blank=True, null=True)
    name = models.CharField(max_length=50, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        return self.product.name

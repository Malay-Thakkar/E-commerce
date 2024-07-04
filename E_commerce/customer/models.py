from django.contrib.auth.models import AbstractUser
from django.db import models
from payment.models import ShippingAddressModel


# customuser model
class CustomUser(AbstractUser):
    phone = models.CharField(max_length=12, blank=True)
    Address = models.TextField(blank=True)
    tandc = models.CharField(blank=True)
    old_cart = models.CharField(max_length=250, blank=True)
    old_wishlist = models.CharField(max_length=250, blank=True)
    shipping_address_model = models.ForeignKey(
        ShippingAddressModel, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Add any other custom fields you need
    def __str__(self):
        return self.username

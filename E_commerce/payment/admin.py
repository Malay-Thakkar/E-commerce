from django.contrib import admin
from .models import Payment, Order, OrderItems, ShippingAddressModel

# Register your models here.

admin.site.register(Payment)
admin.site.register(Order)
admin.site.register(OrderItems)
admin.site.register(ShippingAddressModel)

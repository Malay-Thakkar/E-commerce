from django.urls import path, include
from api.views import ProductViewSet, CategoryViewSet, uploadproductfile, export_products_csv
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static


# Create a router
router = routers.DefaultRouter()

# Register ViewSets with the router
router.register(r"product", ProductViewSet)
router.register(r"category", CategoryViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("uploadproduct", uploadproductfile, name="uploadproductfile"),
    path('export-products/', export_products_csv, name='export_products_csv'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

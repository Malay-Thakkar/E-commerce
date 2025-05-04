from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib import messages
import pandas as pd
from api.models import ProductModel, CategoryModel, UploadProduct
from api.serializers import ProductSerializers, CategorySerializers
from .tasks import process_product_csv
from  .utils import *
import zipfile
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
import csv
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.authentication import TokenAuthentication


# Create your views here.


# ViewSet for handling ProductModel instances
class ProductViewSet(viewsets.ModelViewSet):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializers
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


# ViewSet for handling CategoryModel instances
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = CategoryModel.objects.all()
    serializer_class = CategorySerializers

    # Custom action to retrieve products belonging to a specific category
    @action(detail=True, methods=["get"])
    def product(self, request, pk=None):
        category = CategoryModel.objects.get(pk=pk)
        filter_product = ProductModel.objects.filter(category=category)
        filter_product_serializers = ProductSerializers(
            filter_product, many=True, context={"request": request}
        )
        return Response(filter_product_serializers.data)

@login_required(login_url="/signin")
def uploadproductfile(request):
    if request.user.is_staff and request.method == "POST":
        uploaded_file = request.FILES.get("csv_file")

        if not uploaded_file:
            messages.error(request, "No file selected.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        # Validate file extension
        if not uploaded_file.name.endswith(".csv"):
            messages.error(request, "Please upload a CSV file.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        # Check CSV headers
        try:
            df = pd.read_csv(uploaded_file)
        except Exception:
            messages.error(request, "Unable to read the CSV file. Make sure it's properly formatted.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        if not all(header in df.columns for header in expected_headers):
            print("CSV headers are not properly formatted", df.columns, expected_headers)
            messages.error(request, "CSV headers are not properly formatted.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        # Save and pass to celery
        obj = UploadProduct.objects.create(file=uploaded_file)
        images_zip = request.FILES.get('zip_file')
        
        if images_zip:
            # Ensure the 'uploads' directory exists in MEDIA_ROOT
            upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            zip_file_path = os.path.join(upload_dir, "product_images.zip")

            # Save zip file to the server (temporarily)
            with open(zip_file_path, 'wb') as f:
                for chunk in images_zip.chunks():
                    f.write(chunk)

            # Extract zip file
            extracted_images = extract_images_from_zip(zip_file_path)

            # Store images using Django's default storage (either local or S3)
            for image_path in extracted_images:
                with open(image_path, 'rb') as image_file:
                    file_name = os.path.basename(image_path)
                    file = ContentFile(image_file.read(), name=file_name)
                    # Save to storage (server or S3 based on settings)
                    storage_path = default_storage.save(f"product_images/{file_name}", file)
                    # Optionally delete the image after uploading
                    os.remove(image_path)
            
            # Process CSV in background
            process_product_csv.delay(obj.file.path, user_email=request.user.email)
            messages.success(request, "CSV uploaded. Processing in background.")
            return redirect("/admin/products/")
        else:
            messages.error(request, "No images zip file selected.")
            return redirect(request.META.get("HTTP_REFERER", "/"))
    else:
        messages.error(request, "Unauthorized or invalid request.")
        return redirect("/")


def extract_images_from_zip(zip_file_path):
    """
    Extract images from the uploaded zip file and return a list of image paths.
    """
    extracted_images = []
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        extracted_folder = os.path.join(settings.MEDIA_ROOT, "uploads", "extracted_images")
        os.makedirs(extracted_folder, exist_ok=True)

        zip_ref.extractall(extracted_folder)
        
        # Iterate through the extracted files
        for file_name in zip_ref.namelist():
            # Full file path in the extracted folder
            file_path = os.path.join(extracted_folder, file_name)

            # Check if it's a file and not a directory
            if os.path.isfile(file_path):
                extracted_images.append(file_path)

    return extracted_images

@staff_member_required  # Ensure that only staff members can access this feature
def export_products_csv(request):
    # Query the products (or any model you're exporting)
    products = ProductModel.objects.all()  # Modify this as needed (e.g., filter, paginate)
    
    # Prepare the HTTP response with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    
    writer = csv.writer(response)
    
    # Write the header row (this will match the columns you need)
    writer.writerow(['ID', 'Name', 'Category', 'Price', 'Stock', 'Product_IMG'])
    
    # Write the product data rows
    for product in products:
        writer.writerow([product.product_id, product.name, product.category.category, product.price, product.stock, product.img if product.img else ''])
    
    return response
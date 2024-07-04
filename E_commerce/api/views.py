from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib import messages
import pandas as pd
from api.models import ProductModel, CategoryModel, UploadProduct
from api.serializers import ProductSerializers, CategorySerializers

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


# Function view for uploading a CSV file containing product data
@login_required(login_url="/signin")
def uploadproductfile(request):
    if request.user.is_staff:
        if request.method == "POST":
            file = request.FILES["files"]
            obj = UploadProduct.objects.create(file=file)
            # Call function to create database entries from the uploaded file
            create_db(obj.file)

            messages.success(request, "product added successfully!!!")
            return redirect("/admin/products/")
        else:
            return messages.error(request, "Invalid request method")
    else:
        return redirect("/")


# Function to create database entries from a CSV file
def create_db(file_path):
    # Define expected column headers in the CSV file
    expected_headers = [
        "Product_Name",
        "Product_Stock",
        "Product_Desc",
        "Product_Img",
        "Product_Price",
        "Product_Unit",
        "category_id",
    ]
    try:
        df = pd.read_csv(file_path)
        # Check if all expected headers are present in the CSV file
        if not all(header in df.columns for header in expected_headers):
            raise ValueError("CSV headers are not properly formatted")

        # Iterate through each row in the DataFrame
        for index, row in df.iterrows():
            try:
                # create objects
                ProductModel.objects.create(
                    name=row["Product_Name"],
                    price=row["Product_Price"],
                    unit=row["Product_Unit"],
                    stock=row["Product_Stock"],
                    desc=row["Product_Desc"],
                    img=row["Product_Img"],
                    category=get_object_or_404(CategoryModel, pk=row["category_id"]),
                )
            except Exception as e:
                print(f"Error processing row {index + 1}: {str(e)}")
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")

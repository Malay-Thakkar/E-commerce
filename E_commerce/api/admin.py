from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget
from api.models import ProductModel, CategoryModel

# Resource classes for Import/Export
class ProductResource(resources.ModelResource):
    # Use a custom field for the foreign key conversion:
    category = Field(
        column_name='category',  # CSV header
        attribute='category',   
        widget=ForeignKeyWidget(CategoryModel, 'category')
    )
    
    class Meta:
        model = ProductModel
        import_id_fields = ('name',)
        fields = (
            "name",
            "price",
            "unit",
            "stock",
            "desc",
            "img",
            "category",
        )
        export_order = (
            "name",
            "price",
            "unit",
            "stock",
            "desc",
            "img",
            "category",
        )
    
    def before_import_row(self, row, **kwargs):
        print(f"Importing row: {row}")  # Optionally log each row import
        return row

class CategoryResource(resources.ModelResource):
    class Meta:
        model = CategoryModel
        # Use 'category' as the identifier field for import
        import_id_fields = ('category',)
        # Only include the relevant field in the import/export process
        fields = ('category',)
        export_order = ('category',)


    def before_import_row(self, row, **kwargs):
        print(f"Importing row: {row}")  # Logs each row being processed
        return row


# Admin Classes
@admin.register(ProductModel)
class ProductModelAdmin(ImportExportModelAdmin):
    list_display = [
        field.name for field in ProductModel._meta.fields if field.name != "category"
    ] + ["category_name"]  # Add category_name to list_display

    search_fields = ["name", "category__category"]
    list_filter = ["category"]
    resource_class = ProductResource

    def category_name(self, obj):
        return obj.category.category if obj.category else None

    category_name.short_description = "Category"

@admin.register(CategoryModel)
class CategoryModelAdmin(ImportExportModelAdmin):
    list_display = ['category']  # Only show the 'category' field in the admin panel
    search_fields = ['category']
    resource_class = CategoryResource

from django.contrib import admin
from api.models import ProductModel, CategoryModel

# Register your models here.
admin.site.register(CategoryModel)


@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = [
        field.name for field in ProductModel._meta.fields if field.name != "category"
    ]
    search_fields = ["name", "category__category"]  # Search by name and category
    list_filter = ["category"]  # Filter by category

    def category_name(self, obj):
        return obj.category.category if obj.category else None

    category_name.short_description = "Category"

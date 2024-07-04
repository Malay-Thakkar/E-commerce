from rest_framework import serializers
from api.models import ProductModel, CategoryModel


# category hyperlink serializer(help with url redirect)
class CategorySerializers(serializers.HyperlinkedModelSerializer):
    category_id = serializers.ReadOnlyField()

    class Meta:
        model = CategoryModel
        fields = "__all__"


# Product hyperlink serializer(help with url redirect)
class ProductSerializers(serializers.HyperlinkedModelSerializer):
    product_id = serializers.ReadOnlyField()

    class Meta:
        model = ProductModel
        fields = "__all__"

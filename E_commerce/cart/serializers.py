from rest_framework import serializers

class CartWishlistSerializer(serializers.Serializer):
    """
    Serializer for validating the product_id for cart and wishlist actions.
    """
    product_id = serializers.IntegerField(required=True)

# This serializer is used for actions that require updating the quantity.
class CartUpdateSerializer(serializers.Serializer):
    """
    Serializer for validating data when updating cart item quantity.
    """
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)


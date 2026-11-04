
"""Serializers for the eCommerce REST API."""

from rest_framework import serializers

from .models import Store, Product, Review


class StoreSerializer(serializers.ModelSerializer):
    """Serialize store data for API requests and responses."""

    class Meta:
        """Define the fields exposed by the store serializer."""

        model = Store
        fields = ['id', 'vendor', 'name', 'description']
        read_only_fields = ['id', 'vendor']


class ProductSerializer(serializers.ModelSerializer):
    """Serialize product data for API requests and responses."""

    class Meta:
        """Define the fields exposed by the product serializer."""

        model = Product
        fields = [
            'id',
            'store',
            'name',
            'description',
            'price',
            'stock',
        ]
        read_only_fields = ['id', 'store']


class ReviewSerializer(serializers.ModelSerializer):
    """Serialize reviews with their product and store names."""

    product_name = serializers.CharField(
        source='product.name',
        read_only=True,
    )
    store_name = serializers.CharField(
        source='product.store.name',
        read_only=True,
    )

    class Meta:
        """Define the fields exposed by the review serializer."""

        model = Review
        fields = [
            'id',
            'product',
            'product_name',
            'store_name',
            'user',
            'rating',
            'comment',
            'is_verified',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'is_verified',
            'created_at',
        ]

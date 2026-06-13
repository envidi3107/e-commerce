from rest_framework import serializers
from .models import Category, Product, ProductImage, Inventory


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model  = Category
        fields = ['id', 'name', 'slug', 'code', 'description', 'image', 'is_active', 'product_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_product_count(self, obj):
        return obj.products.filter(status='active').count()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ProductImage
        fields = ['id', 'image_url', 'alt_text', 'order']


class InventorySerializer(serializers.ModelSerializer):
    available = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()

    class Meta:
        model  = Inventory
        fields = ['quantity', 'reserved', 'available', 'low_stock_threshold', 'is_low_stock', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_code = serializers.CharField(source='category.code', read_only=True)
    images        = ProductImageSerializer(many=True, read_only=True)
    inventory     = InventorySerializer(read_only=True)

    class Meta:
        model  = Product
        fields = [
            'id', 'category', 'category_name', 'category_code',
            'name', 'slug', 'description', 'price', 'compare_price',
            'sku', 'status', 'thumbnail', 'attributes',
            'rating_avg', 'rating_count',
            'images', 'inventory',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'rating_avg', 'rating_count', 'created_at', 'updated_at']


class ProductWriteSerializer(serializers.ModelSerializer):
    """Used for create/update - excludes nested read-only."""
    class Meta:
        model  = Product
        fields = [
            'category', 'name', 'slug', 'description',
            'price', 'compare_price', 'sku', 'status',
            'thumbnail', 'attributes',
        ]

    def create(self, validated_data):
        product = Product.objects.create(**validated_data)
        # Auto-create inventory
        Inventory.objects.create(product=product)
        return product


class InventoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Inventory
        fields = ['quantity', 'low_stock_threshold']

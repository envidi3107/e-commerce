from django.contrib import admin
from .models import Category, Product, ProductImage, Inventory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'code', 'is_active', 'created_at')
    list_filter   = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ('name', 'category', 'price', 'status', 'created_at')
    list_filter   = ('status', 'category')
    search_fields = ('name', 'sku')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'reserved', 'available', 'updated_at')

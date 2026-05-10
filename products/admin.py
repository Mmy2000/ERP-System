from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'category', 'cost_price', 'selling_price', 'stock_qty', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['sku', 'name']
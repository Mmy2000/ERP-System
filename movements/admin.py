from django.contrib import admin
from .models import StockMovement

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'qty', 'movement_type', 'reference', 'user', 'timestamp']
    list_filter = ['movement_type', 'timestamp']
    search_fields = ['product__name', 'reference']
    readonly_fields = ['timestamp']
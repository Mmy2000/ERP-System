from django.contrib import admin
from .models import SalesOrder, SalesOrderItem


class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 0
    readonly_fields = ['total']

    def total(self, obj):
        return obj.total
    total.short_description = 'Line Total'


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'order_date', 'status', 'total_amount', 'created_by']
    list_filter = ['status', 'order_date']
    search_fields = ['order_number', 'customer__name']
    inlines = [SalesOrderItemInline]
    readonly_fields = ['order_number', 'total_amount', 'created_at']
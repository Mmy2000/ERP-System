from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_code', 'name', 'email', 'phone', 'opening_balance', 'is_active']
    search_fields = ['customer_code', 'name', 'email']
    list_filter = ['is_active']
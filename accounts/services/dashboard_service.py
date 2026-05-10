from django.utils import timezone
from django.db.models import Sum, Count, Q
from decimal import Decimal


class DashboardService:
    """Service layer for dashboard statistics."""

    @staticmethod
    def get_stats():
        from customers.models import Customer
        from orders.models import SalesOrder
        from products.models import Product

        today = timezone.now().date()

        total_customers = Customer.objects.filter(is_active=True).count()

        total_sales_today = SalesOrder.objects.filter(
            order_date=today,
            status='confirmed'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

        orders_today = SalesOrder.objects.filter(order_date=today, status='confirmed').count()

        low_stock_products = Product.objects.filter(stock_qty__lte=10, is_active=True)
        low_stock_count = low_stock_products.count()

        total_products = Product.objects.filter(is_active=True).count()

        pending_orders = SalesOrder.objects.filter(status='pending').count()

        confirmed_orders = SalesOrder.objects.filter(status='confirmed').count()

        recent_orders = SalesOrder.objects.select_related(
            'customer', 'created_by'
        ).order_by('-created_at')[:5]

        return {
            'total_customers': total_customers,
            'total_sales_today': total_sales_today,
            'orders_today': orders_today,
            'low_stock_count': low_stock_count,
            'low_stock_products': low_stock_products[:5],
            'total_products': total_products,
            'pending_orders': pending_orders,
            'confirmed_orders': confirmed_orders,
            'recent_orders': recent_orders,
        }
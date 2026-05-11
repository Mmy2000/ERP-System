from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class SalesOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=50, unique=True, editable=False)
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT)
    order_date = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_number} - {self.customer.name}'
    

    def recalculate_total(self):
        from django.db.models import Sum, F, ExpressionWrapper, DecimalField
        result = self.items.aggregate(
            total=Sum(
                ExpressionWrapper(F('qty') * F('price'), output_field=DecimalField())
            )
        )
        self.total_amount = result['total'] or 0
        self.save(update_fields=['total_amount'])


class SalesOrderItem(models.Model):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    qty = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ['order', 'product']

    def __str__(self):
        return f'{self.order.order_number} - {self.product.name} x{self.qty}'

    @property
    def total(self):
        return self.qty * self.price
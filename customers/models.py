from django.db import models


class Customer(models.Model):
    customer_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.customer_code} - {self.name}'

    @property
    def total_orders(self):
        return self.salesorder_set.exclude(status='cancelled').count()

    @property
    def total_spent(self):
        from django.db.models import Sum
        result = self.salesorder_set.filter(status='confirmed').aggregate(
            total=Sum('total_amount')
        )
        return result['total'] or 0
    
    @property
    def balance(self):
        """Opening balance minus total confirmed order amounts."""
        from django.db.models import Sum
        confirmed_total = self.salesorder_set.filter(
            status='confirmed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        return self.opening_balance - confirmed_total
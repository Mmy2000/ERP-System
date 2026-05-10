from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('sale', 'Sale'),
        ('return', 'Return / Cancellation'),
        ('adjustment', 'Manual Adjustment'),
        ('purchase', 'Purchase / Restock'),
    ]

    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, related_name='movements')
    qty = models.IntegerField(help_text='Positive = stock in, Negative = stock out')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    reference = models.CharField(max_length=100, blank=True, help_text='e.g. Order number')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        direction = 'IN' if self.qty > 0 else 'OUT'
        return f'{direction} {abs(self.qty)}x {self.product.name} ({self.reference})'
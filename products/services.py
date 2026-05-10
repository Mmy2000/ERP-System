from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Product


class ProductService:
    """All business logic for the Product module."""

    @staticmethod
    def get_all_active():
        return Product.objects.filter(is_active=True)

    @staticmethod
    def get_by_id(product_id):
        return Product.objects.get(pk=product_id, is_active=True)

    @staticmethod
    def search(query=None, category=None):
        qs = Product.objects.filter(is_active=True)
        if query:
            qs = qs.filter(name__icontains=query) | Product.objects.filter(
                sku__icontains=query, is_active=True
            )
        if category:
            qs = qs.filter(category__iexact=category)
        return qs.distinct()

    @staticmethod
    def get_categories():
        return Product.objects.filter(is_active=True).values_list(
            'category', flat=True
        ).distinct().order_by('category')

    @staticmethod
    @transaction.atomic
    def create(data: dict) -> Product:
        product = Product(**data)
        product.full_clean()
        product.save()
        return product

    @staticmethod
    @transaction.atomic
    def update(product: Product, data: dict) -> Product:
        for field, value in data.items():
            setattr(product, field, value)
        product.full_clean()
        product.save()
        return product

    @staticmethod
    @transaction.atomic
    def delete(product: Product) -> None:
        product.is_active = False
        product.save(update_fields=['is_active'])

    @staticmethod
    @transaction.atomic
    def adjust_stock(product: Product, quantity: int, user=None) -> Product:
        """
        Adjust stock by quantity (positive = add, negative = subtract).
        Raises ValidationError if stock would go negative.
        """
        new_qty = product.stock_qty + quantity
        if new_qty < 0:
            raise ValidationError(
                f'Insufficient stock for {product.name}. '
                f'Available: {product.stock_qty}, Requested: {abs(quantity)}'
            )
        product.stock_qty = new_qty
        product.save(update_fields=['stock_qty'])
        return product

    @staticmethod
    def get_low_stock(threshold=10):
        return Product.objects.filter(is_active=True, stock_qty__lte=threshold)
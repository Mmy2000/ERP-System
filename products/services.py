from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Product
import hashlib

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
    def generate_image_hash(image):
        hasher = hashlib.sha256()

        for chunk in image.chunks():
            hasher.update(chunk)

        image.seek(0)

        return hasher.hexdigest()

    @staticmethod
    def get_existing_image(image, exclude_product=None):
        """
        Return existing product image if already uploaded before.
        """
        if not image:
            return None, None

        image_hash = ProductService.generate_image_hash(image)

        qs = Product.objects.filter(image_hash=image_hash)

        if exclude_product:
            qs = qs.exclude(pk=exclude_product.pk)

        existing_product = qs.first()

        if existing_product:
            return existing_product.image, image_hash

        return image, image_hash
    
    @staticmethod
    @transaction.atomic
    def create(data: dict) -> Product:

        image = data.get('image')

        if image:
            image_file, image_hash = (
                ProductService.get_existing_image(image)
            )

            data['image'] = image_file
            data['image_hash'] = image_hash

        product = Product(**data)

        product.full_clean()
        product.save()

        return product

    @staticmethod
    @transaction.atomic
    def update(product: Product, data: dict) -> Product:

        image = data.get('image')

        if image:
            image_file, image_hash = (
                ProductService.get_existing_image(
                    image,
                    exclude_product=product
                )
            )

            data['image'] = image_file
            data['image_hash'] = image_hash

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
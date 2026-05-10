from .models import StockMovement


class StockMovementService:
    """Service layer for stock movement logging."""

    @staticmethod
    def log(product, qty: int, movement_type: str, reference: str = '', user=None, notes: str = '') -> StockMovement:
        """Create a stock movement log entry."""
        return StockMovement.objects.create(
            product=product,
            qty=qty,
            movement_type=movement_type,
            reference=reference,
            user=user,
            notes=notes,
        )

    @staticmethod
    def get_all():
        return StockMovement.objects.select_related('product', 'user').all()

    @staticmethod
    def get_for_product(product):
        return StockMovement.objects.filter(product=product).select_related('user').order_by('-timestamp')

    @staticmethod
    def search(query=None, movement_type=None, product_id=None):
        qs = StockMovement.objects.select_related('product', 'user')
        if query:
            qs = qs.filter(reference__icontains=query) | \
                 StockMovement.objects.filter(
                     product__name__icontains=query
                 ).select_related('product', 'user')
        if movement_type:
            qs = qs.filter(movement_type=movement_type)
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs.distinct().order_by('-timestamp')
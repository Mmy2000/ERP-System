from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from movements.services import StockMovementService

from .models import SalesOrder, SalesOrderItem
from products.services import ProductService


class OrderService:
    """All business logic for Sales Orders."""

    @staticmethod
    def generate_order_number():
        today = timezone.now()
        prefix = f'SO-{today.strftime("%Y%m%d")}'
        last = SalesOrder.objects.filter(
            order_number__startswith=prefix
        ).order_by('-order_number').first()

        if last:
            try:
                seq = int(last.order_number.split('-')[-1]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1
        return f'{prefix}-{seq:04d}'

    @staticmethod
    def get_all():
        return SalesOrder.objects.select_related('customer', 'created_by').all()

    @staticmethod
    def get_by_id(order_id):
        return SalesOrder.objects.select_related(
            'customer', 'created_by'
        ).prefetch_related('items__product').get(pk=order_id)

    @staticmethod
    def search(query=None, status=None, customer_id=None):
        qs = OrderService.get_all()
        if query:
            qs = qs.filter(order_number__icontains=query) | \
                 SalesOrder.objects.filter(customer__name__icontains=query).select_related('customer', 'created_by')
        if status:
            qs = qs.filter(status=status)
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        return qs.distinct().order_by('-created_at')

    @staticmethod
    @transaction.atomic
    def create_order(customer, items_data: list, user, notes='') -> SalesOrder:
        """
        Create a new sales order with items.
        items_data: [{'product': Product, 'qty': int, 'price': Decimal}]
        """
        if not items_data:
            raise ValidationError('Order must have at least one item.')

        order = SalesOrder.objects.create(
            order_number=OrderService.generate_order_number(),
            customer=customer,
            created_by=user,
            status='pending',
            notes=notes,
        )

        for item_data in items_data:
            SalesOrderItem.objects.create(
                order=order,
                product=item_data['product'],
                qty=item_data['qty'],
                price=item_data['price'],
            )

        order.recalculate_total()
        return order

    @staticmethod
    @transaction.atomic
    def confirm_order(order: SalesOrder, user) -> SalesOrder:
        """Confirm order and reduce stock."""
        if order.status != 'pending':
            raise ValidationError(f'Cannot confirm an order with status: {order.status}')
        
        # check customer balance
        if order.customer.balance < order.total_amount:
            raise ValidationError(
                f'Insufficient customer balance. '
                f'Balance: {order.customer.balance:.2f}, '
                f'Order total: {order.total_amount:.2f}'
            )

        # Validate stock availability first
        for item in order.items.select_related('product'):
            if item.product.stock_qty < item.qty:
                raise ValidationError(
                    f'Insufficient stock for "{item.product.name}". '
                    f'Available: {item.product.stock_qty}, Required: {item.qty}'
                )

        # Deduct stock and log movements
        for item in order.items.select_related('product'):
            ProductService.adjust_stock(item.product, -item.qty, user=user)
            StockMovementService.log(
                product=item.product,
                qty=-item.qty,
                movement_type='sale',
                reference=order.order_number,
                user=user,
            )

        order.status = 'confirmed'
        order.save(update_fields=['status'])
        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(order: SalesOrder, user) -> SalesOrder:
        """Cancel order and restore stock if was confirmed."""

        if order.created_by != user and not user.is_superuser:
            raise ValidationError('You do not have permission to cancel this order.')
        if order.status == 'cancelled':
            raise ValidationError('Order is already cancelled.')

        was_confirmed = order.status == 'confirmed'

        order.status = 'cancelled'
        order.save(update_fields=['status'])

        # Restore stock only if order was confirmed
        if was_confirmed:
            for item in order.items.select_related('product'):
                ProductService.adjust_stock(item.product, item.qty, user=user)
                StockMovementService.log(
                    product=item.product,
                    qty=item.qty,
                    movement_type='return',
                    reference=order.order_number,
                    user=user,
                )

        return order

    @staticmethod
    @transaction.atomic
    def update_order_items(order: SalesOrder, items_data: list) -> SalesOrder:
        """Update items on a pending order."""
        if order.status != 'pending':
            raise ValidationError('Can only edit pending orders.')

        order.items.all().delete()
        for item_data in items_data:
            SalesOrderItem.objects.create(
                order=order,
                product=item_data['product'],
                qty=item_data['qty'],
                price=item_data['price'],
            )
        order.recalculate_total()
        return order
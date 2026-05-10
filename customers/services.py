from django.db import transaction
from .models import Customer


class CustomerService:
    """All business logic for the Customer module."""

    @staticmethod
    def get_all_active():
        return Customer.objects.filter(is_active=True)

    @staticmethod
    def get_by_id(customer_id):
        return Customer.objects.get(pk=customer_id, is_active=True)

    @staticmethod
    def search(query=None):
        qs = Customer.objects.filter(is_active=True)
        if query:
            qs = qs.filter(name__icontains=query) | Customer.objects.filter(
                customer_code__icontains=query, is_active=True
            ) | Customer.objects.filter(
                email__icontains=query, is_active=True
            )
        return qs.distinct()

    @staticmethod
    def generate_customer_code():
        """Auto-generate next customer code."""
        last = Customer.objects.order_by('-id').first()
        if last:
            try:
                num = int(last.customer_code.split('-')[-1]) + 1
            except (ValueError, IndexError):
                num = Customer.objects.count() + 1
        else:
            num = 1
        return f'CUST-{num:04d}'

    @staticmethod
    @transaction.atomic
    def create(data: dict) -> Customer:
        if not data.get('customer_code'):
            data['customer_code'] = CustomerService.generate_customer_code()
        customer = Customer(**data)
        customer.full_clean()
        customer.save()
        return customer

    @staticmethod
    @transaction.atomic
    def update(customer: Customer, data: dict) -> Customer:
        for field, value in data.items():
            setattr(customer, field, value)
        customer.full_clean()
        customer.save()
        return customer

    @staticmethod
    @transaction.atomic
    def delete(customer: Customer) -> None:
        customer.is_active = False
        customer.save(update_fields=['is_active'])
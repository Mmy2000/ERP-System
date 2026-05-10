from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Product
from customers.models import Customer

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with demo data'

    def handle(self, *args, **options):
        # Create superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created superuser: admin / admin123'))

        # Create a sales user
        if not User.objects.filter(username='sales').exists():
            User.objects.create_user('sales', 'sales@example.com', 'sales123')
            self.stdout.write(self.style.SUCCESS('Created sales user: sales / sales123'))

        # Create products
        products_data = [
            {'sku': 'LAPTOP-001', 'name': 'Dell Laptop 15"', 'category': 'Electronics', 'cost_price': 600, 'selling_price': 899, 'stock_qty': 25},
            {'sku': 'PHONE-001', 'name': 'Samsung Galaxy A54', 'category': 'Electronics', 'cost_price': 250, 'selling_price': 399, 'stock_qty': 50},
            {'sku': 'DESK-001', 'name': 'Standing Desk Pro', 'category': 'Furniture', 'cost_price': 180, 'selling_price': 299, 'stock_qty': 8},
            {'sku': 'CHAIR-001', 'name': 'Ergonomic Office Chair', 'category': 'Furniture', 'cost_price': 120, 'selling_price': 199, 'stock_qty': 15},
            {'sku': 'MONITOR-001', 'name': '27" 4K Monitor', 'category': 'Electronics', 'cost_price': 300, 'selling_price': 449, 'stock_qty': 5},
            {'sku': 'HEADSET-001', 'name': 'Wireless Headset', 'category': 'Accessories', 'cost_price': 40, 'selling_price': 79, 'stock_qty': 100},
            {'sku': 'MOUSE-001', 'name': 'Mechanical Keyboard', 'category': 'Accessories', 'cost_price': 35, 'selling_price': 65, 'stock_qty': 80},
            {'sku': 'TABLET-001', 'name': 'iPad Air 10.9"', 'category': 'Electronics', 'cost_price': 400, 'selling_price': 599, 'stock_qty': 3},
        ]

        for p in products_data:
            Product.objects.get_or_create(sku=p['sku'], defaults=p)
        self.stdout.write(self.style.SUCCESS(f'Created {len(products_data)} products'))

        # Create customers
        customers_data = [
            {'customer_code': 'CUST-0001', 'name': 'TechCorp Inc.', 'email': 'orders@techcorp.com', 'phone': '+1-555-0101', 'opening_balance': 0},
            {'customer_code': 'CUST-0002', 'name': 'Sunrise Retail', 'email': 'purchasing@sunrise.com', 'phone': '+1-555-0202', 'opening_balance': 500},
            {'customer_code': 'CUST-0003', 'name': 'Ahmed Hassan', 'email': 'ahmed@email.com', 'phone': '+20-100-1234567', 'opening_balance': 0},
            {'customer_code': 'CUST-0004', 'name': 'Global Trade LLC', 'email': 'info@globaltrade.com', 'phone': '+1-555-0404', 'opening_balance': 1200},
            {'customer_code': 'CUST-0005', 'name': 'Sara Williams', 'email': 'sara.w@gmail.com', 'phone': '+1-555-0505', 'opening_balance': 0},
        ]

        for c in customers_data:
            Customer.objects.get_or_create(customer_code=c['customer_code'], defaults=c)
        self.stdout.write(self.style.SUCCESS(f'Created {len(customers_data)} customers'))

        self.stdout.write(self.style.SUCCESS('\n✅ Seed complete! Login at /auth/login/ with admin/admin123'))

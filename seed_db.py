import os
import django
from decimal import Decimal
from datetime import datetime

# --- Set up Django environment ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order

def seed():
    # Create single customer
    alice, created = Customer.objects.get_or_create(
        email="alice@example.com",
        defaults={
            "name": "Alice",
            "phone": "+1234567890"
        }
    )
    print(f"Created customer: {alice.name}")

    # Bulk create customers
    bulk_customers_data = [
        {"name": "Bob", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol", "email": "carol@example.com", "phone": None},
    ]

    bulk_customers = []
    for data in bulk_customers_data:
        customer, created = Customer.objects.get_or_create(
            email=data["email"],
            defaults={
                "name": data["name"],
                "phone": data.get("phone")
            }
        )
        bulk_customers.append(customer)
        print(f"Created customer: {customer.name}")

    # Create products
    laptop, created = Product.objects.get_or_create(
        name="Laptop",
        defaults={
            "price": Decimal("999.99"),
            "stock": 10
        }
    )
    tablet, created = Product.objects.get_or_create(
        name="Tablet",
        defaults={
            "price": Decimal("999.99"),
            "stock": 10
        }
    )
    print(f"Created products: {laptop.name}, {tablet.name}")

    # Create order
    order, created = Order.objects.get_or_create(
        customer=alice,
        order_date=datetime.now()
    )
    order.products.set([laptop, tablet])
    print(f"Created order {order.id} for customer {alice.name} with products {[p.name for p in order.products.all()]}")

if __name__ == "__main__":
    seed()
    print("Seeding complete.")

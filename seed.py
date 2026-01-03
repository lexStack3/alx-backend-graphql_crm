from crm.models import Customer, Product, Order
from django.utils import timezone
from decimal import Decimal


def run():
    # Clear existing data (safe for re-runs)
    Order.objects.all().delete()
    Customer.objects.all().delete()
    Product.objects.all().delete()

    # ---- Customers ----
    alice = Customer.objects.create(
        name="Alice",
        email="alice@example.com",
        phone="+1234567890"
    )

    bob = Customer.objects.create(
        name="Bob",
        email="bob@example.com",
        phone="123-456-7890"
    )

    carol = Customer.objects.create(
        name="Carol",
        email="carol@example.com"
    )

    # ---- Products ----
    laptop = Product.objects.create(
        name="Laptop",
        price=Decimal("999.99"),
        stock=10
    )

    phone = Product.objects.create(
        name="Phone",
        price=Decimal("499.99"),
        stock=20
    )

    headset = Product.objects.create(
        name="Headset",
        price=Decimal("79.99"),
        stock=50
    )

    # ---- Orders ----
    order_1 = Order.objects.create(
        customer=alice,
        order_date=timezone.now(),
        total_amount=laptop.price + headset.price
    )
    order_1.products.set([laptop, headset])

    order_2 = Order.objects.create(
        customer=bob,
        order_date=timezone.now(),
        total_amount=phone.price
    )
    order_2.products.set([phone])

    print("Database seeded successfully!")


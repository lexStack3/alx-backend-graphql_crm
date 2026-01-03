from django.db import models


class Customer(models.Model):
    """A model representation of a <Cusgtomer> instance."""
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, blank=False)
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Returns the string representation of a <Customer> instance."""
        return self.name


class Product(models.Model):
    """A model representation of a <Product> instance."""
    name = models.CharField(max_length=100, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        """Return string representation of a <Product> instance."""
        return self.name


class Order(models.Model):
    """A model representation of a <Order> instance."""
    customer = models.ForeignKey(
        Customer,
        blank=False,
        on_delete=models.CASCADE
    )
    products = models.ManyToManyField(
        Product,
        blank=False
    )
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        """Return string representation of a <Order> instance."""
        return f"Order: {self.id}"

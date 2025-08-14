from django.db import models
from django.core.validators import MinValueValidator
from datetime import datetime

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} {self.email}"
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    stock = models.PositiveBigIntegerField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField('Product', related_name='orders')
    order_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"Order #{self.id} for {self.customer.name}"

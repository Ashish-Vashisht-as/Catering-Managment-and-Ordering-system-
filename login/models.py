from django.db import models
from django.contrib.auth.models import User
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/') 
    product_id = models.AutoField(primary_key=True)
    
    class Meta:
        app_label = 'login'

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField('Product', through='CartItem')

    class Meta:
        app_label = 'login'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def get_total_price(self):
        return self.price * self.quantity

    class Meta:
        app_label = 'login'


class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transaction {self.transaction_id}'
    class meta:
        app_label='login'

class CustomerReview(models.Model):
    customer_name = models.CharField(max_length=100)
    review_text = models.TextField()

    def __str__(self):
        return f"{self.customer_name}'s Review"
    class meta:
        app_label='login'
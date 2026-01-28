from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Custom User Model
class User(models.Model):
    username = models.CharField(max_length=20)
    email = models.CharField(max_length=100, unique=True)
    hashedPassword = models.CharField(max_length=255) # Stores the hashed password for security
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

# Model for catalog products
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField() # Available quantity in inventory

    def __str__(self):
        return self.name

# Model representing a user's shopping cart
class Cart(models.Model):
    # OneToOne relation: 1 user has 1 cart
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    
    def __str__(self):
        return f"Cart of {self.user.username}"

# Django Signal: Triggered automatically after a user is created
@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        # Create an empty cart as soon as a new user is registered
        Cart.objects.get_or_create(user=instance)

# Model for individual items inside a cart
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

# Model representing a finalized order
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('crypto', 'Cryptocurrency'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    date_created = models.DateTimeField(auto_now_add=True)

# Model for items linked to an order (preserves price history at time of purchase)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price at the moment of purchase

# Model for tracking cryptocurrency payments
class CryptoPayment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="crypto_payment")
    wallet_address = models.CharField(max_length=255) # Client's wallet address
    crypto_amount = models.DecimalField(max_digits=20, decimal_places=8) # Amount in crypto (e.g., BTC)
    crypto_currency = models.CharField(max_length=10, default='BTC')
    transaction_hash = models.CharField(max_length=255, blank=True, null=True) # Blockchain transaction hash
    is_confirmed = models.BooleanField(default=False) # Reception confirmation
    created_at = models.DateTimeField(auto_now_add=True)

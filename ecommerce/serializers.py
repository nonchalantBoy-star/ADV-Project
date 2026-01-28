from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import Product, User, Cart, Order, CartItem, OrderItem, CryptoPayment

# Serializer for the Product model
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__' # Expose all fields of the model

# Serializer for displaying user information (Read-only)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at']

# Serializer dedicated to user registration (Write-only for password)
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        # Automatic hashing of the password before saving
        password = validated_data.pop('password')
        validated_data['hashedPassword'] = make_password(password)
        return super().create(validated_data)

# Serializer for user login (Simple field validation)
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

# Serializer for items in the cart (with product details)
class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_name', 'product_price', 'quantity']
        read_only_fields = ['id', 'cart']

# Serializer for the complete shopping cart
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True) # Nested list of cart items
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'user_email', 'items']
        read_only_fields = ['id', 'user', 'items']

# Serializer for items within an order
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']

# Main Serializer for the Order model
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_price', 'status', 'payment_method', 'date_created']
        read_only_fields = ['id', 'items', 'total_price', 'date_created']

# Serializer for cryptocurrency payments
class CryptoPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoPayment
        fields = '__all__'
        read_only_fields = ['id', 'order', 'is_confirmed', 'created_at'] # order handled via URL
    

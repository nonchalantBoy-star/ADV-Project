from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import Product, User, Cart, Order, CartItem, OrderItem, CryptoPayment

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        # On mappe 'password' vers 'hashedPassword' dans le modèle
        password = validated_data.pop('password')
        validated_data['hashedPassword'] = make_password(password)
        return super().create(validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_name', 'product_price', 'quantity']
        read_only_fields = ['id', 'cart']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'user_email', 'items']
        read_only_fields = ['id', 'user', 'items']

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_price', 'status', 'payment_method', 'date_created']
        read_only_fields = ['id', 'items', 'total_price', 'date_created']

class CryptoPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoPayment
        fields = '__all__'
        read_only_fields = ['id', 'order', 'is_confirmed', 'created_at']
    

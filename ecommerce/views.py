from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product, User, Cart, Order, CartItem, OrderItem, CryptoPayment
from .serializers import (
    ProductSerializer, UserSerializer, CartSerializer, CartItemSerializer, 
    OrderSerializer, RegisterSerializer, LoginSerializer, CryptoPaymentSerializer
)
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from decimal import Decimal
import secrets # For generating secure random transaction hashes

# --- AUTHENTICATION ---

# Registration of a new user
@extend_schema(request=RegisterSerializer)
@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": "User created", "user_id": user.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Login
@extend_schema(request=LoginSerializer)
@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Invalid email"}, status=status.HTTP_404_NOT_FOUND)

    # Password hash verification
    if not check_password(password, user.hashedPassword):
        return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)

    user_data = UserSerializer(user).data
    return Response({"message": "Login successful", "user": user_data})

# --- PRODUCTS ---

# Get all products (Public)
@api_view(['GET'])
def getAllProducts(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

# Get a specific product by its ID (Public)
@api_view(['GET'])
def getProduct(request, productId):
    product = get_object_or_404(Product, id=productId)
    serializer = ProductSerializer(product)
    return Response(serializer.data)

# Create a new product (Admin)
@extend_schema(request=ProductSerializer)
@api_view(['POST'])
def createProduct(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Update an existing product (Admin)
@extend_schema(request=ProductSerializer)
@api_view(['PATCH'])
def updateProduct(request, productId):
    product = get_object_or_404(Product, id=productId)
    serializer = ProductSerializer(product, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete a product (Admin)
@api_view(['DELETE'])
def deleteProduct(request, productId):
    product = get_object_or_404(Product, id=productId)
    product.delete()
    return Response({"message": "Product deleted"}, status=status.HTTP_200_OK)

# --- CART ---

# Get the contents of a user's cart
@api_view(['GET'])
def getCart(request, userId):
    user = get_object_or_404(User, id=userId)
    cart, created = Cart.objects.get_or_create(user=user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)

# Add an item to the cart (or increase quantity if already present)
@extend_schema(request=CartItemSerializer)
@api_view(['POST'])
def addCartItem(request, userId):
    user = get_object_or_404(User, id=userId)
    cart, created = Cart.objects.get_or_create(user=user)
    
    serializer = CartItemSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        
        # Intelligent duplicate handling in the cart
        item, item_created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
        if not item_created:
            item.quantity += quantity
            item.save()
            
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Remove a specific item from the cart
@api_view(['DELETE'])
def deleteCartItem(request, userId, itemId):
    item = get_object_or_404(CartItem, id=itemId, cart__user_id=userId)
    item.delete()
    return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)

# Completely clear a user's cart
@api_view(['DELETE'])
def clearCart(request, userId):
    cart = get_object_or_404(Cart, user_id=userId)
    cart.items.all().delete()
    return Response({"message": "Cart cleared"}, status=status.HTTP_200_OK)

# --- ORDERS & PAYMENTS ---

# Convert cart into an order and deduct stock
@api_view(['POST'])
def createOrder(request, userId):
    user = get_object_or_404(User, id=userId)
    cart = get_object_or_404(Cart, user=user)
    
    if not cart.items.exists():
        return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
    
    # 1. Stock verification for ALL products in the cart
    for item in cart.items.all():
        if item.product.stock < item.quantity:
            return Response({
                "error": f"Insufficient stock for product '{item.product.name}'",
                "available_stock": item.product.stock
            }, status=status.HTTP_400_BAD_REQUEST)

    # 2. Total price calculation and effective stock deduction
    total_price = 0
    order_items_to_create = []
    
    for item in cart.items.all():
        item.product.stock -= item.quantity
        item.product.save()
        
        total_price += item.product.price * item.quantity
        order_items_to_create.append({
            'product': item.product,
            'quantity': item.quantity,
            'price': item.product.price
        })

    # 3. Creation of the main order
    order = Order.objects.create(user=user, total_price=total_price, status='pending')
    
    # 4. Creation of order detail lines
    for oi in order_items_to_create:
        OrderItem.objects.create(
            order=order,
            product=oi['product'],
            quantity=oi['quantity'],
            price=oi['price']
        )
    
    # 5. Clear cart after successful order creation
    cart.items.all().delete()
    
    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

# See all orders for a user
@api_view(['GET'])
def getOrders(request, userId):
    orders = Order.objects.filter(user_id=userId)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

# Initiate a cryptocurrency payment for an order (Fixed to USDT)
@extend_schema(
    request=CryptoPaymentSerializer,
    responses={201: CryptoPaymentSerializer}
)
@api_view(['POST'])
def payWithCrypto(request, orderId):
    order = get_object_or_404(Order, id=orderId)
    if order.status != 'pending':
        return Response({"error": "Order is already processed"}, status=400)
    
    serializer = CryptoPaymentSerializer(data=request.data)
    if serializer.is_valid():
        # Generate a simulated 64-character blockchain transaction hash
        simulated_hash = secrets.token_hex(32)
        
        # Automatically set the amount in USDT (1:1 ratio with USD/Price)
        payment = serializer.save(
            order=order, 
            crypto_amount=order.total_price, 
            crypto_currency='USDT',
            transaction_hash=simulated_hash
        )
        order.payment_method = 'crypto'
        order.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Simulate confirmation of a crypto payment (Blockchain Confirmation)
@api_view(['POST'])
def confirmCryptoPayment(request, orderId):
    order = get_object_or_404(Order, id=orderId)
    payment = get_object_or_404(CryptoPayment, order=order)
    
    payment.is_confirmed = True
    payment.save()
    
    # Update order status once paid
    order.status = 'paid'
    order.save()
    
    return Response({"message": "Payment confirmed, order is now paid"})

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

# --- AUTHENTICATION ---

@extend_schema(request=RegisterSerializer)
@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": "User created", "user_id": user.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    if not check_password(password, user.hashedPassword):
        return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)

    user_data = UserSerializer(user).data
    return Response({"message": "Login successful", "user": user_data})

# --- PRODUCTS ---

@api_view(['GET'])
def getAllProducts(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getProduct(request, productId):
    product = get_object_or_404(Product, id=productId)
    serializer = ProductSerializer(product)
    return Response(serializer.data)

@extend_schema(request=ProductSerializer)
@api_view(['POST'])
def createProduct(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(request=ProductSerializer)
@api_view(['PATCH'])
def updateProduct(request, productId):
    product = get_object_or_404(Product, id=productId)
    serializer = ProductSerializer(product, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def deleteProduct(request, productId):
    product = get_object_or_404(Product, id=productId)
    product.delete()
    return Response({"message": "Product deleted"}, status=status.HTTP_200_OK)

# --- CART ---

@api_view(['GET'])
def getCart(request, userId):
    user = get_object_or_404(User, id=userId)
    cart, created = Cart.objects.get_or_create(user=user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)

@extend_schema(request=CartItemSerializer)
@api_view(['POST'])
def addCartItem(request, userId):
    user = get_object_or_404(User, id=userId)
    cart, created = Cart.objects.get_or_create(user=user)
    
    serializer = CartItemSerializer(data=request.data)
    if serializer.is_valid():
        # Check if item already exists in cart
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        
        item, item_created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
        if not item_created:
            item.quantity += quantity
            item.save()
            
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def deleteCartItem(request, userId, itemId):
    item = get_object_or_404(CartItem, id=itemId, cart__user_id=userId)
    item.delete()
    return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def clearCart(request, userId):
    cart = get_object_or_404(Cart, user_id=userId)
    cart.items.all().delete()
    return Response({"message": "Cart cleared"}, status=status.HTTP_200_OK)

# --- ORDERS & PAYMENTS ---

@api_view(['POST'])
def createOrder(request, userId):
    user = get_object_or_404(User, id=userId)
    cart = get_object_or_404(Cart, user=user)
    
    if not cart.items.exists():
        return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
    
    # 1. Vérification des stocks d'abord
    for item in cart.items.all():
        if item.product.stock < item.quantity:
            return Response({
                "error": f"Insufficient stock for product '{item.product.name}'",
                "available_stock": item.product.stock
            }, status=status.HTTP_400_BAD_REQUEST)

    # 2. Calcul du prix total et déduction des stocks
    total_price = 0
    order_items_to_create = []
    
    for item in cart.items.all():
        # Déduire le stock
        item.product.stock -= item.quantity
        item.product.save()
        
        total_price += item.product.price * item.quantity
        order_items_to_create.append({
            'product': item.product,
            'quantity': item.quantity,
            'price': item.product.price
        })

    # 3. Création de la commande
    order = Order.objects.create(user=user, total_price=total_price, status='pending')
    
    for oi in order_items_to_create:
        OrderItem.objects.create(
            order=order,
            product=oi['product'],
            quantity=oi['quantity'],
            price=oi['price']
        )
    
    # 4. Vider le panier
    cart.items.all().delete()
    
    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def getOrders(request, userId):
    orders = Order.objects.filter(user_id=userId)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@extend_schema(
    request=CryptoPaymentSerializer,
    responses={201: CryptoPaymentSerializer}
)
@api_view(['POST'])
def payWithCrypto(request, orderId):
    order = get_object_or_404(Order, id=orderId)
    if order.status != 'pending':
        return Response({"error": "Order is already processed"}, status=400)
    
    # Simulate crypto processing
    # In a real app, we would calculate amount based on actual rate
    serializer = CryptoPaymentSerializer(data=request.data)
    if serializer.is_valid():
        payment = serializer.save(order=order)
        order.payment_method = 'crypto'
        order.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def confirmCryptoPayment(request, orderId):
    order = get_object_or_404(Order, id=orderId)
    payment = get_object_or_404(CryptoPayment, order=order)
    
    # Simulate confirmation from blockchain
    payment.is_confirmed = True
    payment.save()
    
    order.status = 'paid'
    order.save()
    
    return Response({"message": "Payment confirmed, order is now paid"})

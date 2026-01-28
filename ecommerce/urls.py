from django.urls import path
from ecommerce import views

urlpatterns = [
    # AUTH
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),

    # PRODUCTS (PUBLIC)
    path('products/', views.getAllProducts, name='get_products'),
    path('products/<int:productId>/', views.getProduct, name='get_product'),

    # ADMIN / MANAGEMENT
    path('admin/products/create/', views.createProduct, name='admin_create_product'),
    path('admin/products/<int:productId>/update/', views.updateProduct, name='admin_update_product'),
    path('admin/products/<int:productId>/delete/', views.deleteProduct, name='admin_delete_product'),

    # CART (USER)
    path('cart/<int:userId>/', views.getCart, name='get_cart'),
    path('cart/<int:userId>/add/', views.addCartItem, name='add_to_cart'),
    path('cart/<int:userId>/items/<int:itemId>/', views.deleteCartItem, name='remove_from_cart'),
    path('cart/<int:userId>/clear/', views.clearCart, name='clear_cart'),

    # ORDERS & PAYMENTS
    path('orders/<int:userId>/', views.getOrders, name='get_orders'),
    path('orders/<int:userId>/create/', views.createOrder, name='create_order'),
    path('orders/<int:orderId>/pay-crypto/', views.payWithCrypto, name='pay_crypto'),
    path('orders/<int:orderId>/confirm-crypto/', views.confirmCryptoPayment, name='confirm_crypto'),
]

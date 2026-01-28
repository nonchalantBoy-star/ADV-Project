# E-Commerce API Backend

A robust Django REST Framework (DRF) backend for a simplified e-commerce platform. This project features user authentication, a dynamic product catalog, shopping cart management, stock control, and a simulated cryptocurrency payment system.

## 🚀 Features

- **User Authentication**: Secure registration and login with hashed passwords.
- **Product Catalog**: Full CRUD for administrators and browsing for customers.
- **Shopping Cart**: Automated cart creation on signup, with persistent storage of items.
- **Stock Management**: Real-time stock deduction upon order creation with insufficient stock prevention.
- **Order System**: converts cart items into finalized orders with price history preservation.
- **Crypto Payments**: Automated USDT payment flow (amount and transaction hash generated automatically).
- **API Documentation**: Interactive documentation provided by Swagger (drf-spectacular).

## 🛠️ Technology Stack

- **Framework**: Django & Django REST Framework (DRF)
- **Documentation**: drf-spectacular (OpenAPI 3)
- **Database**: MySQL (configured in `settings.py`)
- **Security**: Hashed passwords using Django's `make_password`.

## ⚙️ Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nonchalantBoy-star/ADV-Project.git
   cd ADV-Project
   ```

2. **Install Dependencies**:
   ```bash
   pip install django djangorestframework drf-spectacular mysqlclient
   ```

3. **Database Configuration**:
   - Ensure you have a MySQL server running.
   - Create a database named `monprojet_db`.
   - Update `DATABASES` settings in `projet/settings.py` if your credentials differ.

4. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Start the Server**:
   ```bash
   python manage.py runserver
   ```

## 📖 API Usage (Swagger)

Once the server is running, you can access the interactive API documentation at:
👉 **[http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)**

### Recommended Testing Flow:
1. **Register**: `POST /eshop/register/`
2. **Login**: `POST /eshop/login/`
3. **Create Product (Admin)**: `POST /eshop/admin/products/create/`
4. **Add to Cart**: `POST /eshop/cart/<userId>/add/`
5. **Place Order**: `POST /eshop/orders/<userId>/create/`
6. **Pay (Crypto)**: 
   - `POST /eshop/orders/<orderId>/pay-crypto/`
   - `POST /eshop/orders/<orderId>/confirm-crypto/`

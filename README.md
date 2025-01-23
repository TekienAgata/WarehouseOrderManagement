# Warehouse and Order Management System

A web-based application for managing warehouse inventory and customer orders, with separate interfaces for customers and administrators.

## Features

### Customer Features
1. Product Browsing
   - View available products
   - See product details and stock levels
2. Order Management
   - Add products to cart
   - Place orders
   - View order confirmation

### Administrator Features
1. User Management
   - Create admin users
   - Manage user permissions
2. Product Management
   - Add/Edit products
   - Manage inventory levels
   - Assign products to warehouses
3. Order Management
   - View all orders
   - Update order status
   - Track inventory changes

## Forms and Validation

1. User Registration Form
   - Required fields: username, password
   - Validation: unique username, password requirements

2. Order Placement Form
   - Required fields: customer name, email, product selection
   - Validation: stock availability, valid email format

3. Product Management Form (Admin)
   - Required fields: name, price, stock, warehouse
   - Validation: positive numbers, required fields

## API Endpoints

### Public Endpoints
- `GET /api/products` - List available products
- `POST /api/register` - Create new user account
- `POST /api/login` - User authentication
- `POST /api/orders` - Place new order

### Admin-only Endpoints
- `POST /api/products` - Add new product
- `GET /api/orders` - View all orders

## Database Structure

1. User
   - Properties: id, username, password, is_admin
   - Relations: None

2. Product
   - Properties: id, name, description, price, stock
   - Relations: Warehouse (Many-to-One), Orders (Many-to-Many)

3. Warehouse
   - Properties: id, name, location
   - Relations: Products (One-to-Many)

4. Order
   - Properties: id, customer_name, customer_email, total_price, created_at, shipped
   - Relations: Products (Many-to-Many), OrderItems (One-to-Many)

5. OrderItem
   - Properties: order_id, product_id, quantity
   - Relations: Order (Many-to-One), Product (Many-to-One)

## Security Features

1. JWT Authentication
   - Token-based authentication
   - 1-hour token expiration
   - Secure password hashing

2. Role-based Access Control
   - Public access for product viewing
   - Customer access for ordering
   - Admin access for management features

## Error Handling

- Input validation errors
- Authentication errors
- Database constraints
- Stock availability checks

For installation and configuration instructions, please see [INSTALLATION.md](INSTALLATION.md)

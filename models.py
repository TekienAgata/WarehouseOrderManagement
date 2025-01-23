from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Float,
    Table,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

order_products = Table(
    "order_products",
    db.Model.metadata,
    Column("order_id", Integer, ForeignKey("orders.id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("quantity", Integer, nullable=False),
)


class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)

    def json(self):
        return {
            "id": self.id,
            "username": self.username,
            "is_admin": self.is_admin,
        }


class Product(db.Model):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)

    warehouse = relationship("Warehouse", back_populates="products")

    orders = relationship("Order", secondary=order_products, back_populates="products")

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "stock": self.stock,
            "warehouse_id": self.warehouse_id,
        }


class Warehouse(db.Model):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)

    products = relationship("Product", back_populates="warehouse")

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
        }


class Order(db.Model):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    shipped = Column(Boolean, default=False)

    products = relationship(
        "Product", secondary=order_products, back_populates="orders"
    )
    order_items = relationship("OrderItem", backref="order")

    def json(self):
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "total_price": self.total_price,
            "created_at": self.created_at.isoformat(),
            "shipped": self.shipped,
            "items": [item.json() for item in self.order_items],
        }


class OrderItem(db.Model):
    __tablename__ = "order_items"
    order_id = Column(Integer, ForeignKey("orders.id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    quantity = Column(Integer, nullable=False)

    product = relationship("Product")

    def json(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product.name,
            "quantity": self.quantity,
            "price": self.product.price,
        }

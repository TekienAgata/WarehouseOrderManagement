from app import app, models
from werkzeug.security import generate_password_hash


def init_db():
    with app.app_context():
        models.db.create_all()

        if not models.User.query.filter_by(username="admin").first():
            admin = models.User(
                username="admin",
                password=generate_password_hash("admin123"),
                is_admin=True,
            )
            models.db.session.add(admin)

        warehouse = models.Warehouse.query.filter_by(name="Main Warehouse").first()
        if not warehouse:
            warehouse = models.Warehouse(name="Main Warehouse", location="123 Main St")
            models.db.session.add(warehouse)
            models.db.session.commit()

        if not models.Product.query.first():
            products = [
                models.Product(
                    name="Product 1",
                    description="Description for Product 1",
                    price=19.99,
                    stock=100,
                    warehouse_id=warehouse.id,
                ),
                models.Product(
                    name="Product 2",
                    description="Description for Product 2",
                    price=29.99,
                    stock=50,
                    warehouse_id=warehouse.id,
                ),
            ]
            models.db.session.bulk_save_objects(products)

        models.db.session.commit()


if __name__ == "__main__":
    init_db()
from flask import Flask, jsonify, request, make_response, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
import models
from os import environ
from datetime import timedelta

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg2://{environ.get('POSTGRES_USER')}:"
    f"{environ.get('POSTGRES_PASSWORD')}@{environ.get('POSTGRES_HOST')}:"
    f"{environ.get('POSTGRES_PORT')}/{environ.get('POSTGRES_DB')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = environ.get("JWT_SECRET_KEY", "supersecretkey")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response


models.db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    models.db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        if not data or not data.get("username") or not data.get("password"):
            return make_response(jsonify({"error": "Invalid input"}), 400)

        username = data["username"]
        password = data["password"]

        if models.User.query.filter_by(username=username).first():
            return make_response(jsonify({"error": "Username already exists"}), 400)

        hashed_password = generate_password_hash(password)
        user = models.User(username=username, password=hashed_password)
        models.db.session.add(user)
        models.db.session.commit()

        access_token = create_access_token(
            identity={"id": user.id, "is_admin": user.is_admin}
        )
        return (
            jsonify(
                {"message": "Registration successful", "access_token": access_token}
            ),
            201,
        )
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        if not data or not data.get("username") or not data.get("password"):
            return make_response(
                jsonify({"error": "Nieprawidłowe dane logowania"}), 400
            )

        user = models.User.query.filter_by(username=data["username"]).first()
        if user and check_password_hash(user.password, data["password"]):
            access_token = create_access_token(
                identity={"id": user.id, "is_admin": user.is_admin}
            )
            return (
                jsonify(
                    {
                        "message": "Logowanie udane",
                        "access_token": access_token,
                        "is_admin": user.is_admin,
                    }
                ),
                200,
            )

        return make_response(jsonify({"error": "Nieprawidłowe dane logowania"}), 401)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


@app.route("/api/products", methods=["GET"])
def get_products():
    try:
        products = models.Product.query.filter(models.Product.stock > 0).all()
        return jsonify({"products": [product.json() for product in products]}), 200
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


@app.route("/api/products", methods=["POST"])
@jwt_required()
def create_product():
    try:
        current_user = get_jwt_identity()
        if not current_user["is_admin"]:
            return make_response(jsonify({"error": "Dostęp zabroniony"}), 403)

        data = request.get_json()
        required_fields = ["name", "price", "stock", "warehouse_id"]
        if not all(field in data for field in required_fields):
            return make_response(jsonify({"error": "Brakujące wymagane pola"}), 400)

        product = models.Product(
            name=data["name"],
            description=data.get("description", ""),
            price=float(data["price"]),
            stock=int(data["stock"]),
            warehouse_id=int(data["warehouse_id"]),
        )

        models.db.session.add(product)
        models.db.session.commit()

        return (
            jsonify({"message": "Produkt dodany pomyślnie", "product": product.json()}),
            201,
        )
    except Exception as e:
        models.db.session.rollback()
        return make_response(jsonify({"error": str(e)}), 500)


@app.route("/api/orders", methods=["POST"])
def create_order():
    try:
        data = request.get_json()
        required_fields = ["customer_name", "customer_email", "products"]
        if not all(field in data for field in required_fields):
            return make_response(jsonify({"error": "Brakujące wymagane pola"}), 400)

        total_price = 0
        order_items = []

        for item in data["products"]:
            if not isinstance(item, dict) or not all(
                k in item for k in ["product_id", "quantity"]
            ):
                return make_response(
                    jsonify({"error": "Nieprawidłowy format produktu"}), 400
                )

            product = models.Product.query.get(item["product_id"])
            if not product:
                return make_response(
                    jsonify({"error": f"Produkt {item['product_id']} nie znaleziony"}),
                    400,
                )
            if product.stock < item["quantity"]:
                return make_response(
                    jsonify(
                        {"error": f"Niewystarczająca ilość produktu {product.name}"}
                    ),
                    400,
                )

            total_price += product.price * item["quantity"]
            order_items.append((product, item["quantity"]))

        order = models.Order(
            customer_name=data["customer_name"],
            customer_email=data["customer_email"],
            total_price=total_price,
            shipped=False,
        )
        models.db.session.add(order)
        models.db.session.flush()

        for product, quantity in order_items:
            order_item = models.OrderItem(
                order_id=order.id, product_id=product.id, quantity=quantity
            )
            product.stock -= quantity
            models.db.session.add(order_item)

        models.db.session.commit()

        return (
            jsonify({"message": "Zamówienie złożone pomyślnie", "order": order.json()}),
            201,
        )
    except Exception as e:
        models.db.session.rollback()
        return make_response(jsonify({"error": str(e)}), 500)


@app.route("/api/orders", methods=["GET"])
@jwt_required()
def get_orders():
    try:
        current_user = get_jwt_identity()
        if not current_user["is_admin"]:
            return make_response(jsonify({"error": "Dostęp zabroniony"}), 403)

        orders = models.Order.query.order_by(models.Order.created_at.desc()).all()
        return jsonify({"orders": [order.json() for order in orders]}), 200
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    try:
        product = models.Product.query.get_or_404(product_id)
        return jsonify(product.json()), 200
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


@app.route("/api/products/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    try:
        current_user = get_jwt_identity()
        if not current_user["is_admin"]:
            return make_response(jsonify({"error": "Access forbidden"}), 403)

        product = models.Product.query.get_or_404(product_id)
        data = request.get_json()

        if "name" in data:
            product.name = data["name"]
        if "description" in data:
            product.description = data["description"]
        if "price" in data:
            product.price = data["price"]
        if "stock" in data:
            product.stock = data["stock"]
        if "warehouse_id" in data:
            product.warehouse_id = data["warehouse_id"]

        models.db.session.commit()
        return jsonify({"message": "Product updated", "product": product.json()}), 200
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    try:
        current_user = get_jwt_identity()
        if not current_user["is_admin"]:
            return make_response(jsonify({"error": "Access forbidden"}), 403)

        product = models.Product.query.get_or_404(product_id)
        models.db.session.delete(product)
        models.db.session.commit()
        return jsonify({"message": "Product deleted"}), 200
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

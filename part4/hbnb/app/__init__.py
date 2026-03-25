"""
hbnb/app/__init__.py - Application Factory Pattern
"""
import os
from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from hbnb.config import config

jwt = JWTManager()
bcrypt = Bcrypt()
db = SQLAlchemy()


def create_app(config_name=None):
    """Application factory."""

    # Sélection automatique de la bonne configuration
    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", "default")

    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # Charger la configuration
    app.config.from_object(config[config_name])

    # Initialisation des extensions
    jwt.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)

    # CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Activer les contraintes SQLite (FK)
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    import sqlite3

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    # Import des namespaces API
    from hbnb.app.api.v1.users import api as users_ns
    from hbnb.app.api.v1.places import api as places_ns
    from hbnb.app.api.v1.reviews import api as reviews_ns
    from hbnb.app.api.v1.amenities import api as amenities_ns
    from hbnb.app.api.v1.auth import api as auth_ns

    @app.route("/")
    def home():
        return "Welcome to the HBnB API! Visit /api/v1/docs for documentation."

    # Documentation Swagger
    api = Api(
        app,
        title="HBnB API",
        version="1.0",
        doc="/api/v1/docs",
        validate=False,
    )

    api.add_namespace(users_ns,     path="/api/v1/users")
    api.add_namespace(places_ns,    path="/api/v1/places")
    api.add_namespace(reviews_ns,   path="/api/v1/reviews")
    api.add_namespace(amenities_ns, path="/api/v1/amenities")
    api.add_namespace(auth_ns,      path="/api/v1/auth")

    # Création des tables
    with app.app_context():
        from hbnb.app.models import User, Place, Review, Amenity  # noqa
        db.create_all()

    # Initialisation des données (admin + amenities)
    with app.app_context():
        try:
            from hbnb.app.services import facade
            from hbnb.app.utils import hash_password
            from hbnb.app.models.amenity import Amenity

            # Admin
            if not facade.get_user_by_email("admin@hbnb.io"):
                facade.create_user({
                    "first_name": "Admin",
                    "last_name":  "User",
                    "email":      "admin@hbnb.io",
                    "password":   hash_password("admin1234"),
                    "is_admin":   True,
                })
                print("✅ Admin user created")
            else:
                print("✅ Admin user already exists")

            # Amenities par défaut
            for name in ["WiFi", "Pool", "Parking"]:
                if not Amenity.query.filter_by(name=name).first():
                    db.session.add(Amenity(name=name))

            db.session.commit()

        except Exception as e:
            print(f"Could not initialize database: {e}")

    return app


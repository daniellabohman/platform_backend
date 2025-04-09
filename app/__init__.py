from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from app.models import db  # Import db from models.py (don't redefine it)

# Initialize extensions (Migrate, CORS)
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database and migrations
    db.init_app(app)  
    migrate.init_app(app, db)

    # Initialize JWTManager efter app-konfigurationen
    jwt = JWTManager(app)

    # Importing models inside the function to avoid circular imports
    from app.models import User, Course, Booking, Notification, Category, Instructor

    # Apply migrations (only if necessary)
    with app.app_context():
        db.create_all()  

    # Enable CORS (Cross-Origin Resource Sharing)
    CORS(app, origins=["http://localhost:3000"], supports_credentials=True, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])


    # Import blueprints and register them
    from app.routes import main_routes
    app.register_blueprint(main_routes)

    return app

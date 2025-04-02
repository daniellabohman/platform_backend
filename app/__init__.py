from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

# Initialize the extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database and migrations
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models inside the function to avoid circular imports
    from app.models import User, Course, Booking, Feedback, Category  # <-- Import models here

    # Enable CORS (Cross-Origin Resource Sharing)
    CORS(app)

    # Import blueprints and register them
    from app.routes import main_routes
    app.register_blueprint(main_routes)

    return app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
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

    # Importing models inside the function to avoid circular imports
    from app.models import User, Course, Booking, Feedback, Category

    # Apply migrations (only if necessary)
    with app.app_context():
        db.create_all()  

    # Enable CORS (Cross-Origin Resource Sharing)
    CORS(app)

    # Import blueprints and register them
    from app.routes import main_routes
    app.register_blueprint(main_routes)

    return app

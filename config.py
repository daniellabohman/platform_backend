import os
import pymysql

pymysql.install_as_MySQLdb()

class Config:
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default_secret_key')  # Secret key for JWT, fallback to default if not set

    # Database Configuration (MySQL)
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:UgandaSkipper9@localhost/nexpertia_db"  # Replace with your database connection string
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking to save resources

    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'profile_pics')  # Directory for storing profile pictures
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image file extensions
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Maximum file size: 16MB (can adjust if necessary)

    # Ensure upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

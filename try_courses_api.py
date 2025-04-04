from app import create_app
from app.models import db, Course

# Create app instance
app = create_app()

# Use the app context when working with the database
with app.app_context():
    courses = Course.query.all()  # Querying all courses
    print(courses)

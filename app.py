from app import create_app  # Import the create_app function
from app.models import db  # Import db

# Initialize the app using the create_app function
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

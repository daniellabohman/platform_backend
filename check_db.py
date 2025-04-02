from app import create_app, db  # Import your app creation function and db
from sqlalchemy import inspect  # Import the inspect module

app = create_app()

# Use app context to interact with db
with app.app_context():
    # Get the database engine
    engine = db.engine
    
    # Use SQLAlchemy's inspect method to get the table names
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    
    # Print the table names
    print(table_names)

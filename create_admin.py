from app import create_app, db  # Sørg for at importere din Flask app og db korrekt
from app.models import User
from werkzeug.security import generate_password_hash
from datetime import datetime

# Opret Flask app context
app = create_app()

def create_admin_user():
    username = "admin"
    email = "admin@example.com"
    password = "admin123"

    # Brug app context
    with app.app_context():
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print("Admin user already exists.")
            return

        # Opret admin-bruger
        admin_user1 = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='admin',
            is_instructor=False,
            created_at=datetime.utcnow()
        )

        db.session.add(admin_user1)
        db.session.commit()

        print("✅ Admin user created:", email)

if __name__ == "__main__":
    create_admin_user()

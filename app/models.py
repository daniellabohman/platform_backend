from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

# User model (customers and instructors)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # e.g., 'admin', 'instructor', 'student'
    address = db.Column(db.String(255), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    is_instructor = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # JWT Authentication Token (for login)
    auth_token = db.Column(db.String(255), nullable=True)
    # Subscription info
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    subscription_status = db.Column(db.String(50), nullable=True)  # 'active', 'inactive', 'cancelled'

    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True)
    invoices = db.relationship('Invoice', backref='user', lazy=True)
    instructor = db.relationship('Instructor', uselist=False, back_populates='user', lazy=True) # One-to-one relation

#Instruktor model
class Instructor(db.Model):
    __tablename__ = 'instructors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    expertise = db.Column(db.String(255), nullable=True)
    user = db.relationship('User', foreign_keys=[user_id], back_populates='instructor', lazy=True)

# Profile model for customers and instructors
class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)

    user = db.relationship('User', backref='profile', lazy=True)


# Course model
class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resources = db.Column(db.Text, nullable=True)  # JSON structure with links to videos/documents

    # Relationships
    instructor = db.relationship('User', backref='courses', lazy=True)
    bookings = db.relationship('Booking', backref='course', lazy=True)
    category = db.relationship('Category', backref='courses')

# Category model for courses
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Booking model
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    # Adding fields for calendar sync (Google Calendar integration)
    google_calendar_event_id = db.Column(db.String(255), nullable=True)

# Invoice model (for payments)
class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # 'paid', 'unpaid'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    booking = db.relationship('Booking', backref='invoice')

# Notification model for users
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)  # Meddelelsen som skal sendes til brugeren
    type = db.Column(db.String(50), nullable=False)  # Type af notifikation, f.eks. 'booking', 'payment', 'reminder'
    status = db.Column(db.String(50), nullable=False, default='unread')  # Status for notifikationen, f.eks. 'unread' eller 'read'
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # Tidspunkt for oprettelsen af notifikationen

    # Relationen til User (hvem modtager notifikationen)
    user = db.relationship('User', backref='notifications', lazy=True)

    def __repr__(self):
        return f"<Notification {self.id} - {self.type} - {self.status}>"


# Subscription model (for Stripe integration)
class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_name = db.Column(db.String(50), nullable=False)  # e.g., 'basic', 'premium'
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), nullable=False)  # 'active', 'inactive', 'canceled'
    stripe_subscription_id = db.Column(db.String(255), nullable=True)  # Stripe Subscription ID


    
    # Relationship
    user = db.relationship('User', backref='subscriptions')

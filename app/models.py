from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# usermodel 
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # f.eks. 'admin', 'teacher', 'student'
    address = db.Column(db.String(255), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)  #
    city = db.Column(db.String(100), nullable=True)  #
    phone_number = db.Column(db.String(20), nullable=True)  
    is_instructor = db.Column(db.Boolean, default=False)  
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationen mellem brugere og bookinger
    bookings = db.relationship('Booking', backref='user', lazy=True)

# Coursemodel 
class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    resources = db.Column(db.Text, nullable=True)  # JSON-struktur med links til videoer/dokumenter

    # Relation between courses and bookings
    bookings = db.relationship('Booking', backref='course', lazy=True)

    # Relation to category
    category = db.relationship('Category', backref='courses')

# Category model for courses
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Bookingsmodel
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=db.func.current_timestamp())

# Feedback model for courses
class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Rating fra 1-5
    comment = db.Column(db.Text, nullable=True)

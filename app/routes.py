from flask import Blueprint, jsonify, request
from app.models import db, User, Course, Booking, Feedback, Category
from werkzeug.security import generate_password_hash, check_password_hash
import json

# Create Blueprint for routes
main_routes = Blueprint('main_routes', __name__)

# Define your routes under the Blueprint

@main_routes.route('/')
def home():
    return "Welcome to the home page!"

@main_routes.route('/about')
def about():
    return "This is the about page!"

# Register a new user 
@main_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    password_hash = generate_password_hash(password)
    address = data['address']
    phone_number = data['phone_number']
    is_instructor = data['is_instructor']

    new_user = User(
        username=username, 
        email=email, 
        password_hash=password_hash, 
        address=address, 
        phone_number=phone_number, 
        is_instructor=is_instructor, 
        role='teacher' if is_instructor else 'student'
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

# Login route
@main_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Login successful', 'user_id': user.id, 'role': user.role}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# Create a new course (only for instructors)
@main_routes.route('/courses', methods=['POST'])
def create_course():
    data = request.get_json()
    title = data['title']
    description = data['description']
    price = data['price']
    category_id = data['category_id']
    instructor_id = data['instructor_id']
    resources = json.dumps(data.get('resources', []))

    new_course = Course(
        title=title, 
        description=description, 
        price=price, 
        category_id=category_id, 
        instructor_id=instructor_id,
        resources=resources
    )
    db.session.add(new_course)
    db.session.commit()
    return jsonify({'message': 'Course created successfully'}), 201

from flask import request, jsonify
from app.models import Course, Category

@main_routes.route('/courses', methods=['GET'])
def list_courses():
    # Get the category filter from the query string
    category = request.args.get('category')

    if category:
        try:
            category = int(category)  # Ensure category is an integer
            courses = Course.query.filter_by(category_id=category).all()
        except ValueError:
            return jsonify({"error": "Invalid category ID"}), 400
    else:
        courses = Course.query.all()

    # Prepare the list of courses to return
    courses_list = []
    for course in courses:
        courses_list.append({
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'price': course.price,
            'category': course.category.name,  # Ensure 'category' relationship is set up in Course model
            "instructor": {
                "id": course.instructor.id,
                "username": course.instructor.username
            },
        })

    return jsonify({'courses': courses_list}), 200



# Update a course with new resources
@main_routes.route('/courses/<int:course_id>/add_resources', methods=['POST'])
def add_resources(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'message': 'Course not found'}), 404

    data = request.get_json()
    new_resources = data.get('resources', [])
    
    existing_resources = json.loads(course.resources) if course.resources else []
    updated_resources = existing_resources + new_resources
    course.resources = json.dumps(updated_resources)

    db.session.commit()
    return jsonify({'message': 'Resources updated successfully'}), 200

# Book a course
@main_routes.route('/book', methods=['POST'])
def book_course():
    data = request.get_json()
    user_id = data['user_id']
    course_id = data['course_id']

    new_booking = Booking(user_id=user_id, course_id=course_id)
    db.session.add(new_booking)
    db.session.commit()
    return jsonify({'message': 'Booking successful'}), 201

# Get courses by instructor
@main_routes.route('/instructor/<int:user_id>/courses', methods=['GET'])
def get_courses_by_instructor(user_id):
    courses = Course.query.filter_by(instructor_id=user_id).all()
    courses_list = []
    for course in courses:
        courses_list.append({
            'title': course.title,
            'description': course.description,
            'price': course.price
        })
    return jsonify({'courses': courses_list}), 200

# Feedback for courses
@main_routes.route('/feedback', methods=['POST'])
def post_feedback():
    data = request.get_json()
    user_id = data['user_id']
    course_id = data['course_id']
    rating = data['rating']
    comment = data.get('comment', '')

    new_feedback = Feedback(user_id=user_id, course_id=course_id, rating=rating, comment=comment)
    db.session.add(new_feedback)
    db.session.commit()
    return jsonify({'message': 'Feedback submitted successfully'}), 201

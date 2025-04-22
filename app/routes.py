import datetime
from flask import Blueprint, jsonify, request, app
from flask_login import login_required, current_user
from app.models import db, User, Course, Booking, Notification, Subscription, Invoice, Category, Profile, Instructor, InvoiceTemplateSetting
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from datetime import timedelta
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os


#Indlæs miljøvariabler fra .env filen
load_dotenv()

# Create Blueprint for routes
main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Backend is running'}), 200

@main_routes.route('/about', methods=['GET'])
def about():
    return jsonify({'message': 'Backend is running'}), 200

from flask_jwt_extended import jwt_required, get_jwt_identity

def token_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if current_user is None:
            return jsonify({'message': 'User not found'}), 404
        return f(current_user, *args, **kwargs)
    return decorated_function

# Register a new user 
@main_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Check if data is present
    if not data or not all(k in data for k in ['username', 'email', 'password', 'address', 'phone_number', 'is_instructor']):
        return jsonify({'message': 'Missing required fields'}), 400

    username = data['username']
    email = data['email']
    password = data['password']
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'Email already exists'}), 400

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

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


#@main_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Tjek for nødvendige felter i request body
    if not data or not all(k in data for k in ['email', 'password']):
        return jsonify({'message': 'Missing required fields'}), 400

    email = data['email']
    password = data['password']

    # Find brugeren i databasen
    user = User.query.filter_by(email=email).first()

    # Hvis brugeren findes, og password er korrekt
    if user and check_password_hash(user.password_hash, password):
        # Opret en JWT token
        token = create_access_token(identity=user.id)
        
        # Tjek om brugeren er en admin
        is_admin = user.role == 'admin'

        # Returner token og isAdmin flag
        return jsonify({
            'message': 'Login successful',
            'access_token': token,
            'isAdmin': is_admin  # Tilføj isAdmin info
        }), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@main_routes.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    course_list = []

    for course in courses:
        course_list.append({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "price": course.price,
            "instructor": {
                "id": course.instructor.id,
                "username": course.instructor.username
            }
        })

    return jsonify({"courses": course_list}), 200

@main_routes.route('/courses', methods=["OPTIONS"])
def options_courses():
    return '', 200  # Allow CORS preflight request for this endpoint

# Book a course
@main_routes.route('/book', methods=['POST'])
def book_course():
    data = request.get_json()

    if not data or not all(k in data for k in ['user_id', 'course_id']):
        return jsonify({'message': 'Missing required fields'}), 400

    user_id = data['user_id']
    course_id = data['course_id']

    user = User.query.get(user_id)
    course = Course.query.get(course_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404
    if not course:
        return jsonify({'message': 'Course not found'}), 404

    new_booking = Booking(user_id=user_id, course_id=course_id)

    try:
        db.session.add(new_booking)
        db.session.commit()
        # Create a notification for the user
        notification_message = f"Your booking for the course '{course.title}' was successful."
        create_notification(user_id, notification_message, 'booking')
        return jsonify({'message': 'Booking successful'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

# Create a new notification
def create_notification(user_id, message, notification_type):
    notification = Notification(
        user_id=user_id,
        message=message,
        type=notification_type,
        status='unread'
    )
    db.session.add(notification)
    db.session.commit()

# Get notifications for a user
@main_routes.route('/notifications/<int:user_id>', methods=['GET'])
def get_notifications(user_id):
    notifications = Notification.query.filter_by(user_id=user_id).all()

    if not notifications:
        return jsonify({'message': 'No notifications found'}), 404

    notifications_list = []
    for notification in notifications:
        notifications_list.append({
            'id': notification.id,
            'message': notification.message,
            'type': notification.type,
            'status': notification.status,
            'created_at': notification.created_at
        })
    return jsonify({'notifications': notifications_list}), 200

# Mark notification as read
@main_routes.route('/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_as_read(notification_id):
    notification = Notification.query.get(notification_id)
    if notification:
        notification.status = 'read'
        db.session.commit()
        return jsonify({'message': 'Notification marked as read'}), 200
    return jsonify({'message': 'Notification not found'}), 404

# Create a subscription
@main_routes.route('/subscriptions', methods=['POST'])
def create_subscription():
    data = request.get_json()

    if not data or not all(k in data for k in ['user_id', 'plan_type', 'status']):
        return jsonify({'message': 'Missing required fields'}), 400

    user_id = data['user_id']
    plan_type = data['plan_type']
    status = data['status']
    start_date = data.get('start_date', datetime.utcnow())
    end_date = data.get('end_date', None)

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    new_subscription = Subscription(
        user_id=user_id,
        plan_name=plan_type,
        status=status,
        start_date=start_date,
        end_date=end_date
    )

    try:
        db.session.add(new_subscription)
        db.session.commit()
        return jsonify({'message': 'Subscription created successfully'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating subscription: {str(e)}'}), 500
    
# Opret eller opdater profil (for instruktør og kunde)
@main_routes.route('/profile', methods=['GET', 'POST'])
@login_required
def manage_profile():
    if request.method == 'GET':
        # Returner brugerens profildata
        if current_user.is_instructor:
            # Hvis bruger er instruktør, returner instruktørens profil
            profile = current_user.instructor
        else:
            # Hvis bruger er kunde, returner kundens profil
            profile = current_user.profile
        
        # Returnerer profilens data som JSON
        if profile:
            return jsonify(profile.serialize()), 200
        else:
            return jsonify({"message": "Profile not found"}), 404

    elif request.method == 'POST':
        data = request.get_json()

        # Hvis data mangler
        if not data:
            return jsonify({"message": "No data provided"}), 400

        try:
            if current_user.is_instructor:
                # Hvis det er en instruktør, opdater instruktørens profil
                instructor = current_user.instructor
                instructor.bio = data.get('bio', instructor.bio)
                instructor.expertise = data.get('expertise', instructor.expertise)
            else:
                # Hvis det er en kunde, opdater kundens profil
                profile = current_user.profile
                profile.bio = data.get('bio', profile.bio)
                profile.address = data.get('address', profile.address)
                profile.phone_number = data.get('phone_number', profile.phone_number)
                profile.profile_picture = data.get('profile_picture', profile.profile_picture)

            # Commit ændringerne til databasen
            db.session.commit()

            return jsonify({"message": "Profile updated successfully"}), 200

        except Exception as e:
            # Håndter eventuelle fejl under opdateringen
            db.session.rollback()
            return jsonify({"message": f"Error updating profile: {str(e)}"}), 500


# Get all subscriptions for a user
@main_routes.route('/subscriptions/<int:user_id>', methods=['GET'])
def get_subscriptions(user_id):
    subscriptions = Subscription.query.filter_by(user_id=user_id).all()

    if not subscriptions:
        return jsonify({'message': 'No subscriptions found'}), 404

    subscriptions_list = []
    for subscription in subscriptions:
        subscriptions_list.append({
            'plan_type': subscription.plan_name,
            'status': subscription.status,
            'start_date': subscription.start_date,
            'end_date': subscription.end_date
        })
    return jsonify({'subscriptions': subscriptions_list}), 200


# Create an invoice for a booking
@main_routes.route('/invoices', methods=['POST'])
def create_invoice():
    data = request.get_json()

    # Ensure the required fields are included
    required_fields = ['invoice_number', 'due_date', 'vat_amount', 'cvr_number', 'ean_number', 
                       'payment_method', 'bank_account', 'note', 'pdf_url', 'user_id']

    if not data or not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400

    # Extract data from request
    invoice_number = data['invoice_number']
    due_date = data['due_date']
    vat_amount = data['vat_amount']
    cvr_number = data['cvr_number']
    ean_number = data['ean_number']
    payment_method = data['payment_method']
    bank_account = data['bank_account']
    note = data['note']
    pdf_url = data['pdf_url']
    user_id = data['user_id']

    # Create the invoice object
    new_invoice = Invoice(
        invoice_number=invoice_number,
        due_date=due_date,
        vat_amount=vat_amount,
        cvr_number=cvr_number,
        ean_number=ean_number,
        payment_method=payment_method,
        bank_account=bank_account,
        note=note,
        pdf_url=pdf_url,
        user_id=user_id  # Assuming invoice is tied to a user
    )

    try:
        db.session.add(new_invoice)
        db.session.commit()
        return jsonify({'message': 'Invoice created successfully'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating invoice: {str(e)}'}), 500
    
   
@main_routes.route('/invoices/<int:invoice_id>', methods=['PUT'])
def update_invoice(invoice_id):
    data = request.get_json()

    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return jsonify({'message': 'Invoice not found'}), 404

    # Update invoice fields
    invoice.invoice_number = data.get('invoice_number', invoice.invoice_number)
    invoice.due_date = data.get('due_date', invoice.due_date)
    invoice.vat_amount = data.get('vat_amount', invoice.vat_amount)
    invoice.cvr_number = data.get('cvr_number', invoice.cvr_number)
    invoice.ean_number = data.get('ean_number', invoice.ean_number)
    invoice.payment_method = data.get('payment_method', invoice.payment_method)
    invoice.bank_account = data.get('bank_account', invoice.bank_account)
    invoice.note = data.get('note', invoice.note)

    try:
        db.session.commit()
        return jsonify({'message': 'Invoice updated successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating invoice: {str(e)}'}), 500

    
#Invoice table settings
@main_routes.route('/invoice-template-settings', methods=['POST'])
def create_invoice_template_settings():
    data = request.get_json()

    # Ensure required fields for template settings
    required_fields = ['user_id', 'logo_url', 'custom_text', 'color_theme', 'font_style']

    if not data or not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400

    user_id = data['user_id']
    logo_url = data['logo_url']
    custom_text = data['custom_text']
    color_theme = data['color_theme']
    font_style = data['font_style']

    # Create new template settings
    new_settings = InvoiceTemplateSetting(
        user_id=user_id,
        logo_url=logo_url,
        custom_text=custom_text,
        color_theme=color_theme,
        font_style=font_style
    )

    try:
        db.session.add(new_settings)
        db.session.commit()
        return jsonify({'message': 'Invoice template settings created successfully'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating template settings: {str(e)}'}), 500


# Beskyttet route for admin
@main_routes.route('/admin/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    users = User.query.all()
    return jsonify({'users': [u.serialize() for u in users]})

@main_routes.route('/admin/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    if current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200


@main_routes.route('/instructors', methods=['GET'])
def get_instructors():
    instructors = Instructor.query.all()  # Assuming you have an Instructor model
    if not instructors:
        return jsonify({'message': 'No instructors found'}), 404

    instructors_list = []
    for instructor in instructors:
        instructors_list.append({
            'id': instructor.id,
            'user_id': instructor.user_id,
            'bio': instructor.bio,
            'expertise': instructor.expertise,
            'rate': instructor.rate,
            'profile_picture': instructor.profile_picture
        })
    
    return jsonify({'instructors': instructors_list}), 200


# Create a new instructor
@main_routes.route('/instructors', methods=['POST'])
def create_instructor():
    data = request.get_json()

    if not data or not all(k in data for k in ['user_id', 'bio', 'expertise', 'rate', 'profile_picture']):
        return jsonify({'message': 'Missing required fields'}), 400

    user_id = data['user_id']
    bio = data['bio']
    expertise = data['expertise']
    rate = data['rate']
    profile_picture = data['profile_picture']

    # Make sure user_id exists (check if the user is registered)
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    new_instructor = Instructor(
        user_id=user_id,
        bio=bio,
        expertise=expertise,
        rate=rate,
        profile_picture=profile_picture
    )

    try:
        db.session.add(new_instructor)
        db.session.commit()
        return jsonify({'message': 'Instructor created successfully'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


# Update an instructor's information
@main_routes.route('/instructors/<int:id>', methods=['PUT'])
def update_instructor(id):
    data = request.get_json()

    instructor = Instructor.query.get(id)
    if not instructor:
        return jsonify({'message': 'Instructor not found'}), 404

    # Update fields (you can choose to update only certain fields like bio, rate, etc.)
    instructor.bio = data.get('bio', instructor.bio)
    instructor.expertise = data.get('expertise', instructor.expertise)
    instructor.rate = data.get('rate', instructor.rate)
    instructor.profile_picture = data.get('profile_picture', instructor.profile_picture)

    try:
        db.session.commit()
        return jsonify({'message': 'Instructor updated successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


# Delete an instructor
@main_routes.route('/instructors/<int:id>', methods=['DELETE'])
def delete_instructor(id):
    instructor = Instructor.query.get(id)
    if not instructor:
        return jsonify({'message': 'Instructor not found'}), 404

    try:
        db.session.delete(instructor)
        db.session.commit()
        return jsonify({'message': 'Instructor deleted successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


# Utility function to check if the file is of an allowed type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

# API Endpoint for uploading profile picture
@main_routes.route('/upload_profile_picture', methods=['POST'])
@login_required  # Ensures that only authenticated users can upload pictures
def upload_profile_picture():
    # Check if the file part exists in the request
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    
    file = request.files['file']
    
    # If no file is selected, return error
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    # If the file is allowed, save it
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)  # Secure the filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Construct the full file path
        file.save(file_path)  # Save the file to the defined folder
        
        # Save the file path in the database for the current instructor
        instructor = Instructor.query.get(current_user.id)  # Assuming `current_user.id` is the logged-in instructor
        instructor.profile_picture = f'{request.host_url}static/profile_pics/{filename}'  # URL for the image
        db.session.commit()

        return jsonify({'message': 'Profile picture uploaded successfully', 'url': f'http://localhost:5000/profile_pics/{filename}'}), 200
    else:
        return jsonify({'message': 'Invalid file type. Only PNG, JPG, JPEG, GIF are allowed.'}), 400
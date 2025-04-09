import datetime
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import db, User, Course, Booking, Notification, Subscription, Invoice, Category, Profile
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import create_access_token # type: ignore

# Create Blueprint for routes
main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Backend is running'}), 200

@main_routes.route('/About', methods=['GET'])
def about():
    return jsonify({'message': 'Backend is running'}), 200

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


# Login route
@main_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not all(k in data for k in ['email', 'password']):
        return jsonify({'message': 'Missing required fields'}), 400

    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        token = create_access_token(identity=user.id)
        return jsonify({'message': 'Login successful', 'access_token': token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


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

    if not data or not all(k in data for k in ['booking_id', 'amount', 'status', 'due_date']):
        return jsonify({'message': 'Missing required fields'}), 400

    booking_id = data['booking_id']
    amount = data['amount']
    status = data['status']
    due_date = data['due_date']

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'message': 'Booking not found'}), 404

    new_invoice = Invoice(
        booking_id=booking_id,
        amount=amount,
        status=status,
        due_date=due_date
    )

    try:
        db.session.add(new_invoice)
        db.session.commit()
        return jsonify({'message': 'Invoice created successfully'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating invoice: {str(e)}'}), 500



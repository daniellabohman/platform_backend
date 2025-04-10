from werkzeug.security import generate_password_hash

# List of test users with plain-text passwords
users = [
    {'username': 'janedoe', 'password': 'password123'},
    {'username': 'bobsmith', 'password': 'mypassword'},
    {'username': 'alicejohnson', 'password': 'securepassword!'},
    {'username': 'charliebrown', 'password': 'charlie123'},
]

# Function to hash passwords for all users
def generate_user_hashes(users):
    for user in users:
        hashed_password = generate_password_hash(user['password'])
        print(f"Username: {user['username']}, Hashed Password: {hashed_password}")

# Generate and print password hashes for the test users
generate_user_hashes(users)


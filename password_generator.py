import secrets

# Generer en 32-byte lang sikker JWT secret key
jwt_secret_key = secrets.token_urlsafe(32)

print(jwt_secret_key)  # Udskriv den genererede nøgle


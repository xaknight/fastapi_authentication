from jose import jwt
import secrets
import config
import base64
import os

def generate_state_token():
    """Generates a random state token for CSRF protection."""
    # return secrets.token_urlsafe(32)
    state = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    return state

def create_jwt_token(data: dict):
    """Creates an internal JWT for communication between services."""
    return jwt.encode(data, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
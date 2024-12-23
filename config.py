import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
# This should be the URL of your authentication microservice's callback endpoint
GOOGLE_REDIRECT_URL = "http://auth-service:8001/auth/google/callback"

# Internal JWT Configuration (for communication between services)
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-strong-secret-key")  # Keep this VERY secret!
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
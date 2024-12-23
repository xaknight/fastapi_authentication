from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import requests
import config
from jose import jwt
from datetime import datetime, timedelta
import utils

def get_google_auth_url():
    """Generates the Google authorization URL."""
    params = {
        "client_id": config.GOOGLE_CLIENT_ID,
        "redirect_uri": config.GOOGLE_REDIRECT_URL,
        "response_type": "code",
        "scope": "openid profile email",
        "access_type": "offline",
        "state": utils.generate_state_token(), # Important for CSRF protection!
    }
    return f"{config.GOOGLE_AUTHORIZATION_URL}?{urlencode(params)}"

def handle_google_callback(request: Request, code: str = None, error: str = None, state: str = None):
    """Handles the callback from Google, exchanges code for token, fetches user info."""
    stored_state = request.session.pop('state', None)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Google authentication failed: {error}")
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No authorization code provided.")
    if state is None or state != stored_state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter")

    token_data = {
        "client_id": config.GOOGLE_CLIENT_ID,
        "client_secret": config.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": config.GOOGLE_REDIRECT_URL,
    }
    token_response = requests.post(config.GOOGLE_TOKEN_URL, data=token_data)
    token_response.raise_for_status()
    tokens = token_response.json()

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    user_info_response = requests.get(config.GOOGLE_USER_INFO_URL, headers=headers)
    user_info_response.raise_for_status()
    user_info = user_info_response.json()

    # Create or update user in your database (if you have one in the auth service)

    # Generate internal JWT for your main application
    internal_token_data = {
        "sub": user_info["sub"],  # Use Google's user ID as the subject
        "email": user_info.get("email"),
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
        "exp": datetime.utcnow() + timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    internal_token = utils.create_jwt_token(internal_token_data)

    return internal_token, user_info

def verify_internal_token(token: str):
    """Verifies the internal JWT and returns the payload."""
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal token")
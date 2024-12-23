from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import oauth
import config
import utils

app = FastAPI()

# CORS to allow your main application to communicate with the auth service
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Replace with your main application's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=config.JWT_SECRET_KEY)

@app.get("/login/google")
async def login_google(request: Request):
    auth_url = oauth.get_google_auth_url()
    request.session['state'] = utils.generate_state_token()
    return RedirectResponse(auth_url)

@app.get("/auth/google/callback")
async def auth_google_callback(request: Request, code: str = None, error: str = None, state: str = None):
    internal_token, user_info = oauth.handle_google_callback(request, code, error, state)
    response = JSONResponse(content={"message": "Authentication successful", "user": user_info})
    # Set the internal token in a cookie for your main application to use
    response.set_cookie(
        key="internal_token",
        value=internal_token,
        httponly=True,  # Important for security!
        secure=True, # In production, only transmit over HTTPS
        samesite="lax",  # Adjust according to your needs
        domain="localhost" # Replace with your domain in production
    )
    return response

@app.get("/userinfo")
async def get_user_info(token: str = Depends(oauth.verify_internal_token)):
    # You can fetch additional user data from your database here if needed
    return token

@app.get("/logout")
async def logout(response: JSONResponse):
    response.delete_cookie("internal_token")
    return response
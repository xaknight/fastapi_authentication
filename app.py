from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
import requests

app = FastAPI()

AUTH_SERVICE_URL = "http://auth-service:8001"

async def get_current_user(request: Request):
    internal_token = request.cookies.get("internal_token")
    if not internal_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        response = requests.get(f"{AUTH_SERVICE_URL}/userinfo", headers={"Authorization": f"Bearer {internal_token}"})
        response.raise_for_status()
        user_data = response.json()
        return user_data
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error communicating with auth service: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid authentication token: {e}")

@app.get("/protected")
async def protected_route(user: dict = Depends(get_current_user)):
    return {"message": f"Hello, {user.get('name', 'user')}! This is a protected route."}

@app.get("/login")
async def login():
    return RedirectResponse(f"{AUTH_SERVICE_URL}/login/google")
@app.get("/logout")
async def logout():
    response = RedirectResponse(url=f"{AUTH_SERVICE_URL}/logout")
    response.delete_cookie(key="internal_token")  # Clear the internal token on the client-side
    return response
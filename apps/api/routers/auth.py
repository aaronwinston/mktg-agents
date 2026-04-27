from fastapi import APIRouter, HTTPException, status, Response, Request
from pydantic import BaseModel, EmailStr
import jwt
from datetime import datetime, timedelta
from config import settings
from middleware.rate_limit import limiter

router = APIRouter(prefix="/api/auth", tags=["auth"])

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    org_name: str = ""

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    user_id: str
    org_id: str
    email: str

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/signup", response_model=AuthResponse)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def signup(request: Request, data: SignUpRequest, response: Response):
    """Sign up a new user and return auth token in httpOnly cookie."""

    # Generate IDs (in production, this would create actual user records)
    org_id = "org_" + data.email.split("@")[0] + "_" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
    user_id = data.email.split("@")[0]

    # Create JWT payload
    payload = {
        "sub": user_id,
        "org_id": org_id,
        "role": "owner",
        "email": data.email,
    }
    
    # Create access token
    access_token = create_access_token(data=payload)
    
    # Set httpOnly cookie with security flags
    response.set_cookie(
        key="auth_token",
        value=access_token,
        httponly=True,  # Prevents JavaScript access
        secure=True,    # Only send over HTTPS (use False for localhost dev)
        samesite="strict",  # CSRF protection
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 7 days in seconds
        path="/",
    )
    
    # Also set org_id in a separate cookie for frontend access
    response.set_cookie(
        key="current_org_id",
        value=org_id,
        httponly=False,  # Frontend can read this
        secure=True,
        samesite="strict",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    
    return AuthResponse(
        user_id=user_id,
        org_id=org_id,
        email=data.email,
    )

@router.post("/signin", response_model=AuthResponse)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def signin(request: Request, data: SignInRequest, response: Response):
    """Sign in an existing user and return auth token in httpOnly cookie."""

    # In production, verify credentials against database
    # For now, accept any credentials and create a mock session
    org_id = "org_" + data.email.split("@")[0] + "_" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
    user_id = data.email.split("@")[0]

    # Create JWT payload
    payload = {
        "sub": user_id,
        "org_id": org_id,
        "role": "owner",
        "email": data.email,
    }
    
    # Create access token
    access_token = create_access_token(data=payload)
    
    # Set httpOnly cookie with security flags
    response.set_cookie(
        key="auth_token",
        value=access_token,
        httponly=True,  # Prevents JavaScript access
        secure=True,    # Only send over HTTPS (use False for localhost dev)
        samesite="strict",  # CSRF protection
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 7 days in seconds
        path="/",
    )
    
    # Also set org_id in a separate cookie for frontend access
    response.set_cookie(
        key="current_org_id",
        value=org_id,
        httponly=False,  # Frontend can read this
        secure=True,
        samesite="strict",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    
    return AuthResponse(
        user_id=user_id,
        org_id=org_id,
        email=data.email,
    )

@router.post("/signout")
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def signout(request: Request, response: Response):
    """Sign out user by clearing auth cookies."""
    
    response.delete_cookie(key="auth_token", path="/")
    response.delete_cookie(key="current_org_id", path="/")
    
    return {"status": "success", "message": "Signed out successfully"}

"""Authentication routes for admin login."""

from uuid import uuid4
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from scheduler.db import get_session
from scheduler.domain.models import User
from scheduler.services.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


# Request/Response models
class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_admin: bool


# Helper function to get current user
def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User | None:
    """Get current authenticated user from JWT token.
    
    Returns None if no valid token provided.
    """
    if not token:
        return None
    
    payload = decode_token(token)
    if payload is None:
        return None
    
    user_id = payload.get("sub")
    if user_id is None:
        return None
    
    statement = select(User).where(User.id == user_id)
    return session.exec(statement).first()


def require_auth(token: str | None = Depends(oauth2_scheme)) -> dict:
    """Dependency that requires a valid JWT token.
    
    Validates token signature and expiry, but doesn't require user lookup.
    Returns the decoded token payload.
    Raises 401 if token is invalid or missing.
    """
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


# Endpoints
@router.post("/signup", response_model=TokenResponse)
def signup(request: SignupRequest, session: Session = Depends(get_session)):
    """Create a new admin account."""
    # Check if username already exists
    existing = session.exec(
        select(User).where(User.username == request.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email already exists
    existing = session.exec(
        select(User).where(User.email == request.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        id=str(uuid4()),
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
        is_admin=True,
    )
    session.add(user)
    session.commit()
    
    # Return token
    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """Login and get JWT token."""
    # Find user by username
    statement = select(User).where(User.username == form_data.username)
    user = session.exec(statement).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Return token
    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User | None = Depends(get_current_user),
):
    """Get current user info."""
    if current_user is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_admin=current_user.is_admin,
    )

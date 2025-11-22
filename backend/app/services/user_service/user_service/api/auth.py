from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from user_service.schemas import UserCreate, UserLogin, UserResponse, Token
from user_service.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)
from shared.mongo import get_db
from datetime import datetime
from bson import ObjectId

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
db = get_db()


def _users():
    return db["users"]


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    u = _users().find_one({"_id": ObjectId(user_id)})
    if not u:
        raise credentials_exception
    return {"id": str(u["_id"]), "email": u.get("email"), "full_name": u.get("full_name"), "created_at": u.get("created_at")}


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate):
    """Register a new user."""
    # Check if user already exists
    existing_user = _users().find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    doc = {
        "email": user_data.email,
        "hashed_password": hashed_password,
        "full_name": user_data.full_name,
        "created_at": datetime.utcnow(),
    }
    res = _users().insert_one(doc)
    uid = str(res.inserted_id)

    # Create access token
    access_token = create_access_token(data={"sub": uid})

    return {
        "token": access_token,
        "user": {
            "id": uid,
            "email": doc["email"],
            "full_name": doc.get("full_name"),
            "created_at": doc.get("created_at")
        }
    }


@router.post("/login", response_model=dict)
def login(credentials: UserLogin):
    """Login user and return JWT token."""
    # Find user
    user = _users().find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user.get("hashed_password")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user["_id"])})

    return {
        "token": access_token,
        "user": {
            "id": str(user["_id"]),
            "email": user.get("email"),
            "full_name": user.get("full_name"),
            "created_at": user.get("created_at")
        }
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    return current_user

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from user_service.models import User
from user_service.schemas import UserCreate, UserLogin, UserResponse, Token
from user_service.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)
from shared.database import Database

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
db_instance = Database()


def get_db():
    """Dependency to get database session."""
    return db_instance.get_session()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create access token
    access_token = create_access_token(data={"sub": str(db_user.id)})

    return {
        "token": access_token,
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "created_at": db_user.created_at
        }
    }


@router.post("/login", response_model=dict)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token."""
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "created_at": user.created_at
        }
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

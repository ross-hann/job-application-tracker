
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select   
from schemas import UserCreate, UserResponse, Token as TokenResponse
from auth import hash_password, verify_password, create_access_token, get_current_user
from db_models import User
from database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the user already exists
    existing_user = db.execute(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    # Hash the password
    hashed_password = hash_password(user.password)
    # Create the new user
    new_user = User(
        email=user.email,
        password=hashed_password,
        )
    # Add the user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user         # UserResponse model will automatically exclude the hashed_password field

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Retrieve the user from the database
    db_user = db.execute(select(User).where(User.email == form_data.username)).scalar_one_or_none()
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    # Create an access token
    access_token = create_access_token(db_user.id)
    return TokenResponse(access_token=access_token)
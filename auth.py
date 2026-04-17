# auth.py

import os
from dotenv import load_dotenv

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db_models import User
from database import get_db

# from passlib.context import CryptContext, replaced with the argon2 library for password hashing, which provides strong security for password storage and authentication in the application
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone 

load_dotenv()  # Load environment variables from .env file
# JWT configuration settings, including the secret key used for signing the tokens, the algorithm for encoding and decoding, and the token expiration time, which are essential for secure authentication and authorization in the application
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"  # Algorithm used for encoding and decoding JWT tokens  
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time in minutes, which can be adjusted based on your application's requirements    

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ph = PasswordHasher(
    time_cost=2,  # The time cost parameter controls the amount of time it takes to compute the hash, which can be adjusted to increase the difficulty of brute-force attacks
    memory_cost=65536,  # The memory cost parameter controls the amount of memory used during hashing, which can be adjusted to increase the difficulty of brute-force attacks
    parallelism=8,  # The parallelism parameter controls the number of parallel threads used during hashing, which can be adjusted to increase the difficulty of brute-force attacks
)  # Create an instance of the PasswordHasher class from the argon2 library, which will be used to hash and verify passwords using the Argon2 algorithm, providing strong security for password storage and authentication in the application

# create_access_token generates a JWT token that includes the user's id as the subject (sub) and sets an expiration time for the token based on the current 
# time plus the defined expiration duration, allowing for secure authentication and authorization in the application
def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id), # subject: who the token is about (in this case, the user's id), which can be used to identify the user when the token is decoded and validated
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),  # Set the token to expire after the specified time
        "iat": datetime.now(timezone.utc)  # Include the issued at time for better token management and debugging
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)  # Encode the payload into a JWT token using the secret key and specified algorithm
    return token  # Return the generated access token as a string

def hash_password(password: str) -> str:
    #return pwd_context.hash(password) # Hash the password using bcrypt algorithm
    return ph.hash(password)  # Hash the password using the Argon2 algorithm, which provides strong security for password storage and authentication in the application

def verify_password(password: str, hashed_password: str) -> bool:
    #return pwd_context.verify(password, hashed_password) # Verify the provided password against the hashed password, returns True if they match, False otherwise
    try:
        return ph.verify(hashed_password, password)
    except VerifyMismatchError:
        return False  # Verify the provided password against the hashed password using the Argon2 algorithm, returning True if they match and False if they do not, providing secure authentication in the application

# verifying a JWT token and retrieving the corresponding user from the database, ensuring that only authenticated users can access protected routes in the application
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # Define the OAuth2 password flow, which specifies that clients will obtain tokens by sending a POST request to the /login endpoint with their credentials

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Decode the JWT token using the secret key and specified algorithm to extract the payload
        user_id: str = payload.get("sub")  # Extract the user id from the token's subject (sub) claim
        if user_id is None:
            raise credentials_exception  # If the user id is not present in the token, raise an HTTP 401 Unauthorized exception
    except JWTError:
        raise credentials_exception  # If there is an error decoding the token (e.g., invalid token, expired token), raise an HTTP 401 Unauthorized exception
    user = db.query(User).filter(User.id == int(user_id)).first()  # Query the database to retrieve the user based on the extracted user id from the token
    if user is None:
        raise credentials_exception  # If no user is found with the given id, raise an HTTP 401 Unauthorized exception
    return user  # Return the authenticated user object if the token is valid and the user exists in the database

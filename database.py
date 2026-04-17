# database.py

import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()  # Load environment variables from .env file

# Create an engine, the engine manages the connection pool and database connections
'''
    sqllite:/// = use sqlite database
    . = current directory
    /jobtracker.db = the name of the database file
'''
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}, #sqlite specific argument to allow multiple threads to access the database
    echo=True)     

# Create a configured "Session" class, calling it creates a new session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 

# Create a base class for our models to inherit from
class Base(DeclarativeBase):
    pass

# Helper function to get a database session, used as a dependency in FastAPI endpoints
def get_db():
    db = SessionLocal()  # Create a new database session
    try:
        # The 'yield' in get_db() is how FastAPI's dependency injection works with cleanup. When FastAPI sees 'yield', it pauses the function, runs your endpoint with the session, 
        # then comes back and runs everything after 'yield' (the finally block) once the endpoint finishes. This guarantees the session is always closed.
        yield db  
    finally:
        db.close()  # Ensure the session is closed after use
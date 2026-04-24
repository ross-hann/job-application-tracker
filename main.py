#main.py

from auth import get_current_user
from fastapi import FastAPI, HTTPException, Query, Depends  # FastAPI is the main class for creating the API application, HTTPException is used to raise HTTP exceptions with specific status codes and messages, Query is used to define query parameters for filtering and pagination in the API routes, and Depends is used for dependency injection to manage dependencies in the API routes
from sqlalchemy import Select  # SQLAlchemy is used for database interactions, create_engine is used to create a database engine for connecting to the database, and Column, Integer, String, Date are used to define the database schema for the job applications
from sqlalchemy.orm import Session  # sessionmaker is used to create a session factory for managing database sessions, and Session is the class representing a database session for interacting with the database in the API routes
from typing import Optional
from datetime import date
from enum import Enum  # Enum is used to define the ApplicationStatus enum for representing the status of job applications in a structured way, allowing for better validation and consistency in the API routes
from database import Base, engine, get_db  # Importing the database session helper function, base class for models, and engine from the database module, which will be used to interact with the database once we implement the database functionality in the API routes
from db_models import User, Application  # Importing the User and Application models from the db_models module, which will be used to define the database schema for users and job applications and interact with the database once we implement the database functionality in the API routes
from schemas import ApplicationModel, ApplicationResponseModel, ApplicationStatus, ApplicationUpdate  # Importing the Pydantic models and enum for application status from the schema module, which will be used for request validation and response serialization in the API routes 
from routers import auth_router     # Importing the auth router from the routers module, which will be used to handle authentication-related routes such as user registration and login in the API application
from contextlib import asynccontextmanager

# create an application instance/object    
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables on startup (safe to run multiple times)
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not create database tables on startup: {e}")
        print("App will continue running, but database operations may fail")
    yield
    # Shutdown: cleanup if needed

app = FastAPI(
    #optional fields for API metadata  
    title="Job Application Tracker API",   
    description="API for managing job applications, allowing users to create, read, update, and delete job applications, as well as filter and search through them based on various criteria.", 
    version="1.0.0",
    lifespan=lifespan
)         

# Register routers for authentication and application management, which will handle the respective API routes for user registration, login, and CRUD operations on job applications in a modular way, keeping the main application file organized and maintainable
app.include_router(auth_router.router)  # Include the authentication router, which will handle routes related to user registration and login, allowing for secure authentication and authorization in the API application
#app.include_router(application_router.router)  # Include the application router, which will handle routes related

# Routes
@app.get("/") # define a path operation for the root endpoint
def root():
    return {"message": "Job Application Tracker API!", 
            "docs": "/docs"}   # FASTAPI will automatically convert this dictionary to JSON and return it as the response 

'''
# Commenting this code to replace with query parameters for filtering and pagination in the get_applications route
# Route 1: Get all applications
@app.get("/applications")
def list_applications():
    return applications_db
'''
# Render and Railway deployment health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "service:": "Job Application Tracker API"  }

# Route to get summary count of applications by status
@app.get("/applications/stats")
def get_summary(db: Session = Depends(get_db)):
   # summary = {} # Initialize an empty dictionary to store the count of applications for each status
    summary: dict[str, int] = {} # This also creates an empty dictionary to store the count of applications for each status, but with type annotations to specify that the keys are strings (representing the status) and the values are integers (representing the count of applications for that status)
    for app in db.query(Application).all():
        summary[app.status] = summary.get(app.status, 0) + 1
    return {"Total Applications": db.query(Application).count(), "Summary": summary}  # Return a dictionary containing the total number of applications and a summary of the count of applications for each status, providing an overview of the application data in the system

# Route using query parameters to filter applications by company name, status, and pagination
@app.get('/applications', response_model=list[ApplicationResponseModel])  #response_model parameter is used to specify that the response should be a list of ApplicationResponseModel Pydantic models, which ensures that the response data adheres to the defined schema and includes only the fields specified in the model, providing a consistent and structured format for the API responses when retrieving a list of applications with optional filtering and pagination
def get_applications(
    status:  Optional[ApplicationStatus] = Query(
        None,  
        description='Filter by status',
    ),
    company: Optional[str] = Query(None,  description='Filter by company name'),
    skip:    int           = Query(0,     description='Number of results to skip'),
    limit:   int           = Query(10,    description='Maximum results to return'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)   # requires valid JWT token for authentication, and retrieves the current authenticated user from the database using the get_current_user dependency, ensuring that only authenticated users can access this route to retrieve a list of applications with optional filtering and pagination
):
    query = Select(Application).where(Application.user == current_user.id)  # Start building the query to select applications that belong to the current authenticated user, ensuring that users can only access their own applications when retrieving a list of applications with optional filtering and pagination
    if status:
        query = query.where(Application.status == status)
    if company:
        query = query.where(Application.company.contains(company))
    # Apply pagination
    return db.execute(query.offset(skip).limit(limit)).scalars().all()  # Execute the query with optional filtering by status and company name, and apply pagination using the skip and limit parameters, returning a list of applications that match the specified criteria, which will be filtered through the ApplicationResponseModel Pydantic model to ensure that the response adheres to the defined schema and includes only the fields specified in the model, providing a consistent and structured format for the API responses when retrieving a list of applications with optional filtering and pagination

# Route to get a specific application
@app.get("/applications/{app_id}", response_model=ApplicationResponseModel)  #response_model parameter is used to specify that the response should be filtered through the ApplicationResponseModel Pydantic model, which ensures that the response data adheres to the defined schema and includes only the fields specified in the model, providing a consistent and structured format for the API responses when retrieving a specific application by its ID
def get_application(app_id: int, 
                    db: Session = Depends(get_db), 
                    current_user: User = Depends(get_current_user)):  # Use dependency injection to get a database session for interacting with the database when retrieving a specific application by its ID, allowing for proper management of database connections and transactions in the API route
    app = db.get(Application, app_id)  # Use the database session to retrieve the application from the database by its ID, which will return None if the application is not found
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.user != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the owner of this application")
    return app  # Return the application data, which will be filtered through the ApplicationResponseModel Pydantic model to ensure that the response adheres to the defined schema and includes only the fields specified in the model, providing a consistent and structured format for the API responses when retrieving a specific application by its ID

# Route to create a new application
@app.post("/applications", 
          response_model=ApplicationResponseModel, #filter the response through the ApplicationResponseModel Pydantic model, which ensures that the response data adheres to the defined schema and includes only the fields specified in the model, providing a consistent and structured format for the API responses when creating new applications
          status_code=201)    #specifies that a successful creation of a resource should return a 201 Created status code, which is standard for POST requests that create new resources  
def add_application(application: ApplicationModel, 
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):  # The application parameter is expected to be an instance of the ApplicationModel Pydantic model, which will be automatically validated by FastAPI based on the field definitions and constraints specified in the model
    #new_id = max(app["id"] for app in applications_db) + 1
    new_app = {
        "company": application.company,
        "position": application.position,
        "status": application.status.value,   # Access the value of the ApplicationStatus enum member to store the actual string value in the applications_db, ensuring that the status is stored in a consistent format that can be easily filtered and queried later}
        "notes": application.notes,
        "salary": application.salary,
        "applied_on": str(date.today()),  # Example timestamp for when the application was created, which can be used for tracking and sorting applications based on their creation time in the future when we implement a database and more advanced features
        "user_id": current_user.id  # Associate the application with the current user
    }
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app

# Route to update an application's status
# patch method is used for partial updates to a resource, which is appropriate for updating just the status of an application without needing to send the entire application data
@app.patch("/applications/{app_id}", response_model=ApplicationUpdate)  #filter the response through the ApplicationUpdate Pydantic model, which ensures that the response data adheres to the defined schema and includes only the fields specified in the model, providing a consistent and structured format for the API responses when updating an application's status or other fields)  
def update_application_status(app_id: int, 
                              application: ApplicationUpdate, 
                              db: Session = Depends(get_db),  # The application parameter is expected to be an instance of the ApplicationUpdate Pydantic model, which will be automatically validated by FastAPI based on the field definitions and constraints specified in the model, allowing for partial updates to the application data when updating the status or other fields of an existing application
                              current_user: User = Depends(get_current_user)):  # Use dependency injection to get a database session for interacting with the database when updating an application's status or other fields, allowing for proper management of database connections and transactions in the API route
    existing_app = db.get(Application, app_id)  # Use the database session to retrieve the existing application from the database by its ID, or raise a 404 Not Found HTTP exception if the application is not found
    if not existing_app:
        raise HTTPException(status_code=404, detail="Application not found")
    for field, value in application.dict(exclude_unset=True).items():  # Iterate through the fields and values of the incoming application data, excluding any fields that were not set in the request (i.e., only include fields that were provided in the update request), allowing for partial updates to the application data
        if value is not None:  # Check if the value is not None before updating the existing application, ensuring that only fields with provided values are updated and preventing unintended overwriting of existing data with None values
            existing_app[field] = value.value if isinstance(value, Enum) else value  # Update the existing application with the new value, checking if the value is an instance of an Enum (e.g., ApplicationStatus) and accessing its actual value if it is, to ensure that the status is stored in a consistent format that can be easily filtered and queried later when we implement a database and more advanced features      
    db.commit()
    db.refresh(existing_app)
    return existing_app  # Return the updated application data, which will be filtered through the ApplicationResponseModel Pydantic model to ensure that the response adheres to the defined schema and includes only the fields specified in the model, providing a consistent and structured format for the API responses when updating an application's status or other fields

# Route to delete an application
@app.delete("/applications/{app_id}", status_code=204)  #specifies that a   successful deletion of a resource should return a 204 No Content status code, which indicates that the request was successful but there is no content to return in the response body
def delete_application(app_id: int, 
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):  # Use dependency injection to get a database session for interacting with the database when deleting an application, allowing for proper management of database connections and transactions in the API route
    app = db.get(Application, app_id)  # Use the database session to retrieve the application from the database by its ID, or raise a 404 Not Found HTTP exception if the application is not found
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if not app.user == current_user.id:
        raise HTTPException(status_code=403, detail="You are not the owner of this application")
    db.delete(app)
    db.commit()
    return {"detail": "Application deleted successfully"}

# Route using query parameters to filter applications by status
@app.get("/applications/filter")
def filter_applications(status: Optional[str] = Query(None), 
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    if status is None:
        return db.query(Application).all()
    return db.query(Application).filter(Application.status == status).all()




#main.py

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator, model_validator   # BaseModel is used to define data models for request and response validation, while Field is used to provide additional metadata and validation rules for the fields in the data models
from enum import Enum   # Enum is used to define a set of named constant values, which can be used for validation and to ensure that only valid values are accepted for certain fields (e.g., status of a job application)
from typing import Optional
from datetime import date
from schemas import ApplicationModel, ApplicationResponseModel, ApplicationStatus, ApplicationUpdate  # Importing the Pydantic models and enum for application status from the schema module, which will be used for request validation and response serialization in the API routes 

# create an application instance/object    
app = FastAPI(
    #optional fields for API metadata  
    title="Job Application Tracker API",   
    description="API for managing job applications, allowing users to create, read, update, and delete job applications, as well as filter and search through them based on various criteria.", 
    version="1.0.0" 
)         

# Helper function to find an application by its ID in the in-memory applications_db list, and raise a 404 Not Found HTTP exception if the application is not found, providing a consistent way to handle cases where a requested application does not exist in the system 
def find_or_404(app_id: int):
    for application in applications_db:
        if application["id"] == app_id:
            return application
    raise HTTPException(status_code=404, detail="Application not found")  

# In-memory store for now - this must be replaced with a database in the future
applications_db = [
    {'id': 1, 'company': 'Stripe',  'position': 'Engineer', 'status': ApplicationStatus.APPLIED},
    {'id': 2, 'company': 'Google',  'position': 'PM',       'status': ApplicationStatus.INTERVIEW},
    {'id': 3, 'company': 'Figma',   'position': 'Designer', 'status': ApplicationStatus.OFFER},
]

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

# Route using query parameters to filter applications by company name, status, and pagination
@app.get('/applications', response_model=list[ApplicationResponseModel])  #response_model parameter is used to specify that the response should be a list of ApplicationResponseModel Pydantic models, which ensures that the response data adheres to the defined schema and includes only the fields specified in the model, providing a consistent and structured format for the API responses when retrieving a list of applications with optional filtering and pagination
def get_applications(
    status:  Optional[ApplicationStatus] = Query(
        None,  
        description='Filter by status',
      #  enum=['Applied', 'Interview', 'Offer', 'Rejected', 'Withdrawn']  # Enum validation for status query parameter, ensuring that only valid status values can be used for filtering applications, commented out because we are using the ApplicationStatus enum for validation instead
    ),
    company: Optional[str] = Query(None,  description='Filter by company name'),
    skip:    int           = Query(0,     description='Number of results to skip'),
    limit:   int           = Query(10,    description='Maximum results to return'),
):
    results = list(applications_db)
    # Apply filters
    if status:
        results = [a for a in results if a['status'] == status]
    if company:
        results = [a for a in results if company.lower() in a['company'].lower()]                 
    # Apply pagination
    return results[skip : skip + limit]

# Route to get summary count of applications by status
@app.get("/applications/stats")
def get_summary():
   # summary = {} # Initialize an empty dictionary to store the count of applications for each status
    summary: dict[str, int] = {} # This also creates an empty dictionary to store the count of applications for each status, but with type annotations to specify that the keys are strings (representing the status) and the values are integers (representing the count of applications for that status)
    for app in applications_db:
        summary[app["status"]] = summary.get(app["status"], 0) + 1
    return {"Total Applications": len(applications_db), "Summary": summary}  # Return a dictionary containing the total number of applications and a summary of the count of applications for each status, providing an overview of the application data in the system

# Route to get a specific application
@app.get("/applications/{app_id}", response_model=ApplicationResponseModel)  #response_model parameter is used to specify that the response should be filtered through the ApplicationResponseModel Pydantic model, which ensures that the response data adheres to the defined schema and includes only the fields specified in the model, providing a consistent and structured format for the API responses when retrieving a specific application by its ID
def get_application(app_id: int):
    '''
    for application in applications_db:
        if application["id"] == app_id:
            return application
    raise HTTPException(status_code=404, detail="Application not found")
    '''
    return find_or_404(app_id)  # Use the helper function to find the application by its ID and return it, or raise a 404 Not Found HTTP exception if the application is not found, providing a consistent way to handle cases where a requested application does not exist in the system

# Route to create a new application
@app.post("/applications", 
          response_model=ApplicationResponseModel, #filter the response through the ApplicationResponseModel Pydantic model, which ensures that the response data adheres to the defined schema and includes only the fields specified in the model, providing a consistent and structured format for the API responses when creating new applications
          status_code=201)     #specifies that a successful creation of a resource should return a 201 Created status code, which is standard for POST requests that create new resources  
#def add_application(application: dict): # commented this code to replace with Pydantic model for validation and documentation purposes, which provides a more structured and robust way to handle incoming data for creating new applications, ensuring that the data adheres to the defined schema and constraints specified in the ApplicationModel
def add_application(application: ApplicationModel):  # The application parameter is expected to be an instance of the ApplicationModel Pydantic model, which will be automatically validated by FastAPI based on the field definitions and constraints specified in the model
    new_id = max(app["id"] for app in applications_db) + 1
    new_app = {
        "id": new_id,
        "company": application.company,
        "position": application.position,
        "status": application.status.value,   # Access the value of the ApplicationStatus enum member to store the actual string value in the applications_db, ensuring that the status is stored in a consistent format that can be easily filtered and queried later}
        "notes": application.notes,
        "salary": application.salary,
        "applied_on": str(date.today())  # Example timestamp for when the application was created, which can be used for tracking and sorting applications based on their creation time in the future when we implement a database and more advanced features
    }
    applications_db.append(new_app)
    return new_app

# Route to update an application's status
#patch method is used for partial updates to a resource, which is appropriate for updating just the status of an application without needing to send the entire application data
@app.patch("/applications/{app_id}",
           response_model=ApplicationUpdate)  #filter the response through the ApplicationUpdate Pydantic model, which ensures that the response data adheres to the defined schema and includes only the fields specified in the model, providing a consistent and structured format for the API responses when updating an application's status or other fields)  
def update_application_status(app_id: int, application: ApplicationUpdate):  # The application parameter is expected to be an instance of the ApplicationUpdate Pydantic model, which will be automatically validated by FastAPI based on the field definitions and constraints specified in the model, allowing for partial updates to the application data when updating the status or other fields of an existing application
    existing_app = find_or_404(app_id)  # Use the helper function to find the existing application by its ID, or raise a 404 Not Found HTTP exception if the application is not found, providing a consistent way to handle cases where a requested application does not exist in the system
    for field, value in application.dict(exclude_unset=True).items():  # Iterate through the fields and values of the incoming application data, excluding any fields that were not set in the request (i.e., only include fields that were provided in the update request), allowing for partial updates to the application data
        if value is not None:  # Check if the value is not None before updating the existing application, ensuring that only fields with provided values are updated and preventing unintended overwriting of existing data with None values
            existing_app[field] = value.value if isinstance(value, Enum) else value  # Update the existing application with the new value, checking if the value is an instance of an Enum (e.g., ApplicationStatus) and accessing its actual value if it is, to ensure that the status is stored in a consistent format that can be easily filtered and queried later when we implement a database and more advanced features      
    return existing_app  # Return the updated application data, which will be filtered through the ApplicationResponseModel Pydantic model to ensure that the response adheres to the defined schema and includes only the fields specified in the model, providing a consistent and structured format for the API responses when updating an application's status or other fields

# Route to delete an application
@app.delete("/applications/{app_id}", status_code=204)  #specifies that a   successful deletion of a resource should return a 204 No Content status code, which indicates that the request was successful but there is no content to return in the response body
def delete_application(app_id: int):
    app = find_or_404(app_id)  # Use the helper function to find the application by its ID, or raise a 404 Not Found HTTP exception if the application is not found, providing a consistent way to handle cases where a requested application does not exist in the system
    applications_db.remove(app)  # Remove the application from the in-memory applications_db list, effectively deleting it from the system
    return {"detail": "Application deleted successfully"}

# Route using query parameters to filter applications by status
@app.get("/applications/filter")
def filter_applications(status: Optional[str] = Query(None)):
    if status is None:
        return applications_db
    return [app for app in applications_db if app["status"] == status]




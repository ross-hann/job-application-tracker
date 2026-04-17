# schemas.py

from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict, EmailStr

# Define an enumeration for application status, which can be used for validation and to ensure that only valid status values are accepted when creating or updating job applications
class ApplicationStatus(str, Enum):  
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"

class UserCreate(BaseModel):  # Define a Pydantic model for user creation, which will be used for request validation when creating new users
    email: EmailStr = Field(..., example="user@example.com") # EmailStr is a special type provided by Pydantic that validates that the input is a valid email address, and the Field metadata includes an example value for documentation purposes
    password: str = Field(..., min_length=6, example="strongpassword")  # required field for the user's password with a minimum length of 6 characters and an example value for documentation purposes  

class UserResponse(BaseModel):  # Define a Pydantic model for the response when retrieving user information, which includes the user's id and email but excludes the password for security reasons
    id: int
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)  # allows the model to be created from an object with attributes (e.g., an instance of the User dataclass) rather than just from a dictionary, enabling seamless conversion between the dataclass instances and the Pydantic models for request validation and response serialization

class Token(BaseModel):  # Define a Pydantic model for the response when returning an authentication token, which includes the access token and the token type (e.g., "bearer") for documentation purposes
    access_token: str
    token_type: str = Field(..., example="bearer")  # required field for the type of token being returned, with an example value for documentation purposes

class TokenData(BaseModel):  # Define a Pydantic model for the data contained within the authentication token, which includes the user's email and an optional user id for documentation purposes
    email: Optional[EmailStr] = None
    user_id: Optional[int] = None
    
# INPUT schema — what the client sends in the request body 
# Define a Pydantic model for job applications, which will be used for request validation when creating or updating applications
class ApplicationModel(BaseModel):  
    company: str = Field(..., example="Stripe", min_len=2, max_len=100)  # required field (indicated by ...) and includes an example value for documentation purposes
    position: str = Field(..., example="Software Engineer", min_len=2, max_len=100)  
    status: Optional[ApplicationStatus] = Field(ApplicationStatus.APPLIED, description="The current status of the application", example=ApplicationStatus.APPLIED)  # status of the application, which is optional and defaults to "Applied" if not provided
    notes: Optional[str] = Field(None, example="Applied through referral")  
    salary: Optional[float] = Field(None, example=120000.00, gt=0)  # a validation rule to ensure that the salary is greater than 0
    date_applied: Optional[str] = Field(None, example="2024-06-01")  # Optional field for the date the application was submitted, with an example value in YYYY-MM-DD format for documentation purposes

@field_validator("company", "position")  # Define a field validator for the company and position fields to ensure that they are not empty or just whitespace, providing additional validation beyond the basic string type and length constraints defined in the Field metadata
def not_empty(cls, value):
    if not value.strip():  # Check if the value is empty or consists only of whitespace by stripping leading and trailing whitespace and checking if the resulting string is empty
        raise ValueError("Value cannot be empty or just whitespace")  # Raise a ValueError if the validation fails, which will be handled by FastAPI to return an appropriate error response to the client
    return value  # Return the validated value if it passes the check

# Update Schema — what the client sends in the request body when updating an application, which allows for partial updates to the application data of an existing application
class ApplicationUpdate(BaseModel):  # Define a Pydantic model for updating an application, which allows for partial updates to the application data when updating the status or other fields of an existing application
    status: Optional[ApplicationStatus] = Field(None, description="The new status of the application", example=ApplicationStatus.INTERVIEW)  # Optional field for updating the status of the application, with a description and example value for documentation purposes
    notes: Optional[str] = Field(None, example="Updated notes about the application")  
    salary: Optional[float] = Field(None, example=130000.00, gt=0)  # validation rule to ensure that the salary is greater than 0

# OUTPUT schema — what the API returns in the response body, which includes all the fields from the input schema plus an additional id field to uniquely identify each application
class ApplicationResponseModel(ApplicationModel):  # Define a Pydantic model for the response when retrieving job applications, which extends the ApplicationModel to include an additional id field for uniquely identifying each application
    id: int 
    company: str
    position: str   
    status: ApplicationStatus 
    notes: Optional[str] = None
    salary: Optional[float] = None
    date_applied: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)    # allows the model to be created from an object with attributes (e.g., an instance of the Application dataclass) rather than just from a dictionary, enabling seamless conversion between the dataclass instances and the Pydantic models for request validation and response serialization

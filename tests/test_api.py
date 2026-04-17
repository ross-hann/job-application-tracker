# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from main import app    

client = TestClient(app)  # Create a TestClient instance for testing the FastAPI application defined in main.py

# path tests

def test_create_application(client):
    response = client.post("/applications/", json={
        "company": "Test Company",
        "position": "Software Engineer",
        "status": "applied",
        "notes": "This is a test application.",
        "salary": 120000.00,
        "date_applied": "2024-06-01"
    })  # Send a POST request to the /applications/ endpoint with a JSON payload containing the details of a new job application to create a new application in the system
    assert response.status_code == 201  # Assert that the response status code is 201 Created, indicating that the application was successfully created
    data = response.json()  # Parse the JSON response body into a Python dictionary for further assertions
    assert data["company"] == "Test Company"  # Assert that the company field in the response matches the value sent in the request
    assert data["position"] == "Software Engineer"  # Assert that the position field in the response matches the value sent in the request
    assert data["status"] == "applied"  # Assert that the status field in the response matches the value sent in the request
    assert data["notes"] == "This is a test application."  # Assert that the notes field in the response matches the value sent in the request
    assert data["salary"] == 120000.00  # Assert that the salary field in the response matches the value sent in the request
    assert data["date_applied"] == "2024-06-01"  # Assert that the date_applied field in the response matches the value sent in the request

def test_data_persists_within_test_session(client):
    client.post("/applications/", json={
        "company": "Persistence Test Company",
        "position": "Software Engineer",
        "status": "applied",
        "notes": "This is a test application.",
        "salary": 120000.00,
        "date_applied": "2024-06-01"
    })  # Create a new application to test that data persists within the same test session
    response = client.get("/applications/")  # Send a GET request to retrieve the list
    assert response.status_code == 200  # Assert that the response status code is 200 OK, indicating that the request was successful
    assert len(response.json()) == 1  # Assert that there is exactly one application in the response, which should be true if the previous test created an application successfully and the data persists within the same test session

def test_get_applications():
    response = client.get("/applications/")  # Send a GET request to the /applications/ endpoint to retrieve the list of all job applications in the system
    assert response.status_code == 200  # Assert that the response status code is 200 OK, indicating that the request was successful
    data = response.json()  # Parse the JSON response body into a Python list of dictionaries representing the job applications
    assert isinstance(data, list)  # Assert that the response data is a list, which should contain multiple job applications
    assert len(data) > 0  # Assert that there is at least one application in the response, which should be true if the previous test created an application successfully    

def test_update_application():
    # First, create a new application to update
    create_response = client.post("/applications/", json={
        "company": "Update Test Company",
        "position": "Data Scientist",
        "status": "applied",
        "notes": "This application will be updated.",
        "salary": 110000.00,
        "date_applied": "2024-06-01"
    })  # Send a POST request to create a new job application that will be updated in this test
    assert create_response.status_code == 201  # Assert that the application was created successfully
    created_data = create_response.json()  # Parse the JSON response body to get the details of the created application
    application_id = created_data["id"]  # Extract the id of the created application for use in the update request

    # Now, update the application
    update_response = client.put(f"/applications/{application_id}", json={
        "status": "interview",
        "notes": "Updated notes about the application.",
        "salary": 130000.00,
        "date_applied": "2024-06-02"
    })  # Send a PUT request to update the status, notes, salary, and date_applied of the created application using its id
    assert update_response.status_code == 200  # Assert that the update request was successful
    updated_data = update_response.json()  # Parse the JSON response body to get the details of the updated application
    assert updated_data["status"] == "interview"  # Assert that the status field in the response matches the updated value sent in the request
    assert updated_data["notes"] == "Updated notes about the application."  # Assert that the notes field in the response matches the updated value sent in the request
    assert updated_data["salary"] == 130000.00  # Assert that the salary field in the response matches the updated value sent in the request
    assert updated_data["date_applied"] == "2024-06-02"  # Assert that the date_applied field in the response matches the updated value sent in the request 

def test_create_application_invalid_salary():
    response = client.post("/applications/", json={
        "company": "Invalid Salary Company",
        "position": "Backend Developer",
        "status": "applied",
        "notes": "This application has an invalid salary.",
        "salary": -50000.00,  # Invalid salary value (negative)
        "date_applied": "2024-06-01"
    })  # Send a POST request with an invalid salary value to test the validation logic for the salary field
    assert response.status_code == 422  # Assert that the response status code is 422 Unprocessable Entity, indicating that the validation failed due to the invalid salary value   

def test_update_application_invalid_status():
    # First, create a new application to update
    create_response = client.post("/applications/", json={
        "company": "Invalid Status Company",
        "position": "Frontend Developer",
        "status": "applied",
        "notes": "This application will be updated with an invalid status.",
        "salary": 90000.00,
        "date_applied": "2024-06-01"
    })  # Send a POST request to create a new job application that will be updated with an invalid status in this test
    assert create_response.status_code == 201  # Assert that the application was created successfully
    created_data = create_response.json()  # Parse the JSON response body to get the details of the created application
    application_id = created_data["id"]  # Extract the id of the created application for use in the update request

    # Now, attempt to update the application with an invalid status
    update_response = client.put(f"/applications/{application_id}", json={
        "status": "invalid_status",  # Invalid status value that is not part of the ApplicationStatus enum
        "notes": "Attempting to update with an invalid status.",
        "salary": 95000.00,
        "date_applied": "2024-06-02"
    })  # Send a PUT request with an invalid status value to test the validation logic for the status field
    assert update_response.status_code == 422  # Assert that the response status code is 422 Unprocessable Entity, indicating that the validation failed due to the invalid status value    
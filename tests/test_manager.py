# tests/test_manager.py

import pytest
from manager import ApplicationManager
from exceptions import ApplicationNotFoundError, duplicateApplicationError, InvalidStatusError
from unittest.mock import patch # allow replacing real funtions with mock objects during testing 

# fixture is defined using the @pytest.fixture decorator, and is a funtion that provides shared setup to test, instead of creating a new instance of ApplicationManager in each test, 
# we can use this fixture to get a fresh instance for each test case, improving code reuse and maintainability
@pytest.fixture
def manager():          #tests requests this by using 'manager' as a parameter, and pytest will automatically call this function to provide the necessary setup for the test
    with patch('manager.load_applications', return_value=[]):  #patch is used to replace the load_applications function with a mock that returns an empty list, ensuring that each test starts with a clean slate
        patch('manager.save_applications', return_value=None).start()  #patch is used to replace the save_applications function with a mock that does nothing, preventing actual file I/O during testing
        return ApplicationManager()

# Tests that use the fixture 
def test_add_application(manager):
    app = manager.add_application("Company A", "Software Engineer" )
    assert app.company == "Company A"
    assert app.position == "Software Engineer"
    assert app.status == "Applied"

def test_add_duplicate_application(manager):
    manager.add_application("Company A", "Software Engineer")
    with pytest.raises(duplicateApplicationError):             #assert that the code inside the with block raises a duplicateApplicationError, which is expected when trying to add a duplicate application                         
        manager.add_application("Company A", "Software Engineer")

def test_update_application_status(manager):
    app = manager.add_application("Company A", "Software Engineer")
    updated_app = manager.update_status(app.id, "Interview")
    assert updated_app.status == "Interview"    
 
def test_update_application_status_invalid(manager):
    app = manager.add_application("Company A", "Software Engineer")
    with pytest.raises(InvalidStatusError):  #assert that the code inside the with block raises an InvalidStatusError, which is expected when trying to update an application to an invalid status
        manager.update_status(app.id, "InvalidStatus")

def test_remove_application(manager):
    app = manager.add_application("Company A", "Software Engineer")
    manager.remove_application(app.id)
    with pytest.raises(ApplicationNotFoundError):  #assert that the code inside the with block raises an ApplicationNotFoundError, which is expected when trying to remove an application that has already been removed
        manager.remove_application(app.id)

def test_application_by_status(manager):
    manager.add_application("Company A", "Software Engineer", status="Applied")
    manager.add_application("Company B", "Data Scientist", status="Interview")
    manager.add_application("Company C", "Product Manager", status="Applied")
    
    applied_apps = manager.application_by_status("Applied")
    assert len(applied_apps) == 2
    assert all(app.status == "Applied" for app in applied_apps) 

def test_application_by_status_invalid(manager):
    with pytest.raises(InvalidStatusError):  #assert that the code inside the with block raises an InvalidStatusError, which is expected when trying to filter applications by an invalid status
        manager.application_by_status("InvalidStatus")

def test_list_applications(manager):
    manager.add_application("Company A", "Software Engineer")
    manager.add_application("Company B", "Data Scientist")
    apps = manager.list_applications()
    assert len(apps) == 2
    assert any(app.company == "Company A" and app.position == "Software Engineer" for app in apps)
    assert any(app.company == "Company B" and app.position == "Data Scientist" for app in apps)

def test_search_applications(manager):
    manager.add_application("Company A", "Software Engineer")
    manager.add_application("Company B", "Data Scientist")
    manager.add_application("Company C", "Product Engineer")
    
    results = manager.search_applications("Company A")
    assert len(results) == 1
    assert results[0].company == "Company A"
    
    results = manager.search_applications("Data")
    assert len(results) == 1
    assert results[0].position == "Data Scientist"
    
    results = manager.search_applications("Engineer")
    assert len(results) == 2 
    assert results[0].position == "Software Engineer"
    assert results[1].position == "Product Engineer"
    
    results = manager.search_applications("Nonexistent")
    assert len(results) == 0
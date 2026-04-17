#test_models.py

import pytest
from datetime import date
from models import Application

#Rules for pytest to find your test functions:
#1. Test files should be named starting with "test_" or end with _test.py   
#2. Function must start with "test_" and be defined at the module level (not inside a class or another function).
#3. Use assert statemetns to declare expected outcomes.

'''
#Test the is_active() method to ensure it correctly identifies active and inactive application statuses
def test_is_active():  
    active_app = Application(id=3, company="Active Company", position="Active Position")
    assert active_app.is_active() == True  #Status "Applied" should be active

    active_app.status = "Interview"
    assert active_app.is_active() == True  #Status "Interview" should be active

    active_app.status = "Offered"
    assert active_app.is_active() == True  #Status "Offered" should be active

    inactive_app = Application(id=4, company="Inactive Company", position="Inactive Position", status="Rejected")
    assert inactive_app.is_active() == False  #Status "Rejected" should not be active

    inactive_app.status = "Withdrawn"
    assert inactive_app.is_active() == False  #Status "Withdrawn" should not be active
'''
#the same test as above but using pytest's parametrize feature to run the same test logic with different input values, ensuring that all active statuses are correctly identified as active
@pytest.mark.parametrize("status", ["Applied", "Interview", "Offered"])
def test_is_active_with_various_statuses(status):  
    app = Application(id=5, company="Param Company", position="Param Position", status=status)
    assert app.is_active() == True  #Each of the provided statuses should be active

#Test default values are set correctly when creating a new Application instance 
def test_application_defaults():  
    app = Application(id =1, company="Test Company", position="Test Position")
    assert app.id == 1
    assert app.company == "Test Company"
    assert app.position == "Test Position"
    assert app.status == "Applied"  #Default status should be "Applied"
    assert app.notes == None  #Default notes should be an empty string
    assert app.date_applied == date.today()  #Default date_applied should be today's date

#Test that converting an Application to a dictionary and back to an Application preserves all data correctly
# Application -> to_dict() -> dict -> from_dict() -> Application should be identical 
def test_to_dict_and_back():  
    app = Application(id=2, company="Another Company", position="Another Position", status="Interview", notes="Had a good interview", date_applied=date(2024, 1, 15))
    app_dict = app.to_dict()  #Convert the Application instance to a dictionary
    new_app = Application.from_dict(app_dict)  #Create a new Application instance from the dictionary
    assert new_app.id == app.id
    assert new_app.company == app.company
    assert new_app.position == app.position
    assert new_app.status == app.status
    assert new_app.notes == app.notes
    assert new_app.date_applied == app.date_applied




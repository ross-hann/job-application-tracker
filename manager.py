# manager.py

from models import Application
from exceptions import ApplicationNotFoundError, duplicateApplicationError, InvalidStatusError
from storage import save_applications, load_applications
from typing import List, Optional

class ApplicationManager:     # Manages the collection of job applications, providing methods to add, list, and find applications - all access goes through this class ( via various methods) to ensure data integrity and proper handling of the application collection
    def __init__(self):
        self._applications: List[Application] = load_applications()    # Load existing applications from file on startup, ensuring that the manager has the most up-to-date data when it is initialized

    # Properties
    # properties let you access and modify the applications list (data) while keeping the internal representation hidden, allowing for validation and control over how the applications are accessed and modified
    @property
    def applications(self) -> List[Application]:  # Property to get the list of applications
        return self._applications
    
    @property
    def count(self) -> int:  # Property to get the count of applications
        return len(self._applications)
    
    @property
    def active_applications(self) -> List[Application]:  # Property to get the list of active applications (those that are still in progress)
        return [app for app in self._applications if app.is_active()]
    
    @property
    def active_count(self) -> int:  # Property to get the count of active applications
        return len(self.active_applications)

    @property
    def applications(self, value: List[Application]) -> None:  # Property setter to set the list of applications
        self._applications = value

    #CRUD Methods

    def list_applications(self) -> List[Application]:
        return self._applications
    
    def add_application(self, company: str, position: str, **kwargs) -> Application:    # **kwargs passes extra args like notes, salary, etc. to the Application constructor, allowing for flexible application creation while ensuring that company and position are always provided
        if any(app for app in self._applications if app.company == company and app.position == position):
            raise duplicateApplicationError(f"An application for {position} at {company} already exists.")
        
        new_id = max((app.id for app in self._applications), default=0) + 1  # Generate a new unique ID for the application by finding the maximum existing ID and adding 1, ensuring that each application has a unique identifier
        new_app = Application(id=new_id, company=company, position=position, **kwargs)  # Create a new Application instance with the provided company, position, and any additional keyword arguments (like date_applied, status, notes, salary)
        self._applications.append(new_app)  # Add the new application to the list of applications
        save_applications(self._applications)  # Save the updated list of applications to file to ensure data persistence
        return new_app                                                                                          

    def application_by_status(self, status: str) -> List[Application]:  # Method to filter applications by their status, returning a list of applications that match the specified status
        #return [app for app in self._applications if app.status == status]
        VALID = ['Applied', 'Interview', 'Offer', 'Rejected', 'Withdrawn']
        if status not in VALID:
            raise InvalidStatusError(status)
        apps = []
        for app in self._applications:
            if app.status == status:
                apps.append(app)
        return apps
    
    def update_status(self, id: int, new_status: str) -> Application:  # Method to update the status of an application by its ID, allowing for easy status management of applications
        if new_status not in ['Applied', 'Interview', 'Offer', 'Rejected', 'Withdrawn']:
                raise InvalidStatusError(new_status)
        for app in self._applications:
            if app.id == id:
                app.status = new_status
                save_applications(self._applications)  # Save the updated applications to file after changing the status
                return app
        raise ApplicationNotFoundError(f"Application with ID {id} not found.")   
    
    def remove_application(self, id: int) -> None:  # Method to remove an application by its ID, allowing for easy deletion of applications from the manager
        if not any(app for app in self._applications if app.id == id):
            raise ApplicationNotFoundError(f"Application with ID {id} not found.")
        for i, app in enumerate(self._applications):
            if app.id == id:
                del self._applications[i]  # Remove the application from the list  
        for i, app in enumerate(self._applications, start=1):    # re-assigning the IDs after deletion to maintain sequential order
            app.id = i
        save_applications(self._applications)
        return self._applications
    
    # Statistics and Reporting Methods
    def applications_by_company(self) -> dict:  # Method to get a count of applications grouped by company, returning a dictionary where the keys are company names and the values are the counts of applications for each company
        company_counts = {}
        for app in self._applications:
            company_counts[app.company] = company_counts.get(app.company, 1) + 1
        return company_counts
    
    def applications_by_position(self) -> dict:  # Method to get a count of applications grouped by position, returning a dictionary where the keys are position titles and the values are the counts of applications for each position
        position_counts = {}
        for app in self._applications:
            position_counts[app.position] = position_counts.get(app.position, 0) + 1
        return position_counts
    
    def search_applications(self, query: str) -> List[Application]:  # Method to search for applications based on a query string, returning a list of applications where the company or position contains the query string (case-insensitive)
        query_lower = query.lower()
        return [app for app in self._applications if query_lower in app.company.lower() or query_lower in app.position.lower()]
    
    
    
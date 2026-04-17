#models.py

# This file defines the Application dataclass, which represents a job application with attributes like id, company, position, date_applied, status, notes, and salary. Defines what the application data looks like   
# It also includes methods to check if the application is active and to convert the application to and from a dictionary for JSON serialization.

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

@dataclass   # decorator to automatically generate init, repr, etc.
class Application:   # dataclass to represent a job application
    id: int
    company: str
    position: str
    date_applied: date   = field(default_factory=date.today)  # Default to today's date
    status: str          = "Applied"                          # Default status
    notes: Optional[str] = None
    salary: Optional[float] = None   

    def is_active(self) -> bool:    # Method(function that belongs to the class) to check if the application is still active, returns True if the status is one of the active statuses (Applied, Interview, Offered)
        return self.status in ["Applied", "Interview", "Offered"]
    
    def to_dict(self) -> dict:  # Method to convert the application to a dictionary for JSON serialization
        return {
            "id": self.id,
            "company": self.company,
            "position": self.position,
            "date_applied": self.date_applied.isoformat(),
            "status": self.status,
            "notes": self.notes,
            "salary": self.salary
        }

    @classmethod  # called on the class itself, not an instance, to create an Application instance from a dictionary (JSON data)
    def from_dict(cls, data: dict) -> 'Application':  # cls is a reference to the class itself, data is the dictionary containing application data, and it returns an instance of Application
        # Support both new and legacy field names, and tolerate missing date fields.
        date_value = data.get("date_applied") or data.get("data_applied")
        if date_value is not None:
            date_value = date.fromisoformat(date_value)
        else:
            date_value = date.today()
        return cls(
            id=data["id"],
            company=data["company"],
            position=data["position"],
            date_applied=date_value,
            status=data.get("status", "Applied"),
            notes=data.get("notes"),
            salary=data.get("salary")
        )
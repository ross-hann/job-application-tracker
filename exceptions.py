# exceptions.py

class TrackerError(Exception):                                      # base class - inherits from Exception
    pass                                                            # pass = no additional code needed, just a placeholder

class ApplicationNotFoundError(TrackerError):
    """Exception raised when an application is not found."""
    pass

class duplicateApplicationError(TrackerError):
    """Exception raised when a duplicate application is attempted to be added."""
    pass

class InvalidStatusError(TrackerError):
    """Exception raised when an invalid status is provided."""
    VALID = ['Applied', 'Interview', 'Offer', 'Rejected', 'Withdrawn']

    def __init__(self, status):
        self.status = status
        print(f"Invalid status '{status}'. Valid statuses are: {', '.join(self.VALID)}")
        pass
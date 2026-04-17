# storage.py

# Read and wrtie data from/to disk, using JSON format. This file contains functions to save and load applications to a JSON file. 
# The save_applications function takes a list of Application objects, converts them to dictionaries, and saves them to a file. 
# The load_applications function reads the JSON file, converts the dictionaries back to Application objects, and returns a list of applications.


import json
import os
from typing import List
from models import Application

DATA_FILE = "C:\\Users\\amit.roushan\\Desktop\\Job_Tracker\\applications.json"
VALID_STATUSES = ["Applied", "Interview", "Offered", "Rejected", "Withdrawn"]

# ----- Handle data persistence -----

def load_applications() -> List[Application]:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            return [Application.from_dict(item) for item in data]
    return []

def save_applications(applications: List[Application]) -> None:
    data = [app.to_dict() for app in applications]
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

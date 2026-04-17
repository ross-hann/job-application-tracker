#job_tracker_v1.py

import json, os

DATA_FILE = "C:\\Users\\amit.roushan\\Desktop\\Job_Tracker\\applications.json"
VALID_STATUSES = ["Applied", "Interviewing", "Offered", "Rejected", "Withdrawn"]

# ----- Handle data persistence -----

def load_applications():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_applications(apps):
    with open(DATA_FILE, 'w') as f:
        json.dump(apps, f, indent=4)

# --- Core Functions ---

def add_application(apps, company, position, notes=""):
    new_id = max([app["id"] for app in apps], default=0) + 1                                     #auto-increment ID based on existing applications
    app = {
        "id": new_id,
        "company": company,
        "position": position,
        "status": "Applied",
        "notes": notes,       
    }
    apps.append(app)
    save_applications(apps)
    return app

def list_applications(apps):
    for app in apps:
        print(f"Id: {app['id']}, Company: {app['company']}, Position: {app['position']}, Status: {app['status']}, Notes: {app['notes']}")
    if len(apps) == 0:
        print("No applications found.")
    return apps

def filter_by_status(apps, status):
    filtered_apps = [app for app in apps if app['status'] == status]
    for app in filtered_apps:
        print(f"Id: {app['id']}, Company: {app['company']}, Position: {app['position']}, Status: {app['status']}, Notes: {app['notes']}")
    print("Application not found." if len(filtered_apps) == 0 else f"Total applications with status '{status}': {len(filtered_apps)}")

def update_status(apps, id, status):
    for app in apps:
        if app["id"] == id:
            app["status"] = status
            print("Status updated successfully.")
            return app
    print("Application not found.")

def remove_application(apps, id):
    for k, app in enumerate(apps):
        if app['id'] == id:
            del apps[k]
            print("Application removed successfully.")
    for i, app in enumerate(apps, start=1):                                                             #re-assigning the IDs after deletion to maintain sequential order
            app['id'] = i
    save_applications(apps)
    return apps

# -- Main menu loop --

def main():
    apps = load_applications()                                                                          # Load existing applications from file
    while True:
        print("\n ----- Job Application Tracker -----")
        print("1. Add Application")
        print("2. List All Applications")
        print("3. Filter by Status")
        print("4. Update Status")
        print("5. Remove Application")
        print("6. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == '1':
            company = input("Enter company name: ").strip()
            position = input("Enter position: ").strip()
            note = input("Enter any notes (optional): ").strip()
            app = add_application(apps, company, position, note)
            print(f"Application added successfully, company: {app['company']}, position: {app['position']}")
        elif choice == '2':
            list_applications(apps)
        elif choice == '3':
            status = input("Enter status to filter by (Applied/Interviewing/Offered/Rejected/Withdrawn): ").strip()
            filter_by_status(apps, status)
        elif choice == '4':
            id = int(input("Enter application ID to update: ").strip())
            status = input("Enter new status (Applied/Interviewing/Offered/Rejected/Withdrawn): ").strip()
            update_status(apps, id, status)
        elif choice == '5':
            id = int(input("Enter application ID to remove: ").strip())
            remove_application(apps, id)
        elif choice == '6':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":                                                                              # only run main() if this file is run directly
    main()
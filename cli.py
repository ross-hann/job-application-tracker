# cli.py

# Handle user input and command-line interactions. This file contains the main function that serves as the entry point for the application. It provides a simple command-line interface for users to interact with the job tracker

from manager import ApplicationManager
from exceptions import ApplicationNotFoundError, duplicateApplicationError, InvalidStatusError

def main():
    manager = ApplicationManager()
    # Add command-line argument parsing and interaction logic here

    while True:
        print("\n ----- Job Application Tracker -----")
        print("1. List All Applications")
        print("2. Add Application")
        print("3. Filter by Status")
        print("4. Update Status")
        print("5. Remove Application")
        print("6. Applications by Position")
        print("7. Search Application by Company or Position")
        print("8. Exit")
        
        choice = input("\nEnter your choice: ").strip()

        if choice == '1':
            apps = manager.list_applications()
            for app in apps:
                print(app)    
        elif choice == '2':
            company = input("Enter company name: ").strip()
            position = input("Enter position: ").strip()
            notes = input("Enter notes (optional): ").strip()
            try:
                app = manager.add_application(company, position, notes=notes)
                print(f"Application added successfully: {app}")
            except duplicateApplicationError as e:
                print(e)
        elif choice == '3':
            try:
                status = input("Enter status to filter by: ").strip()
                apps = manager.application_by_status(status)
                for app in apps:
                    print(app)
            except InvalidStatusError as e:
                continue
        elif choice == '4':
            try:
                id = int(input("Enter application ID to update: ").strip())
                new_status = input("Enter new status: ").strip()    
                app = manager.update_status(id, new_status)
                print(f"Status updated successfully: {app}")
            except (ApplicationNotFoundError, InvalidStatusError) as e:
                print(e)
        elif choice == '5':
            try:
                id = int(input("Enter application ID to remove: ").strip())
                manager.remove_application(id)
                print("Application removed successfully.")
            except ApplicationNotFoundError as e:
                print(e)
        elif choice == '6':
            apps = manager.applications_by_position()
            for position, count in apps.items():
                print(f"{position}: {count} applications")
        elif choice == '7':
            search_term = input("Enter search term: ").strip()
            apps = manager.search_applications(search_term)
            for app in apps:
                print(app)
        elif choice == '8':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()  
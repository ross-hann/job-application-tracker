import os 
import streamlit as st
import requests

API_URL = os.getenv("API_URL") or "http://localhost:8000"  # your fast api server address

def get_headers() -> dict:
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

# Authentication
def api_register(email: str, password: str) -> dict | None:
    try:
        response = requests.post(f"{API_URL}/auth/register", 
                                 json={"email": email, "password": password}, 
                                 timeout=60
                                 )
        if response.status_code == 201:
            return response.json()
        return None
    except requests.RequestException as e:
        st.error(f"Registration failed: {e}")
        return None
    
def api_login(email: str, password: str) -> dict | None:
    try:
        response = requests.post(f"{API_URL}/auth/login", 
                                 data={"username": email, "password": password}, 
                                 timeout=60
                                 )
        if response.status_code == 200:
            return response.json()
        st.error(f"Backend Error ({response.status_code}): {response.text}")
        return None
    except requests.RequestException as e:
        st.error(f"Login failed: {e}")
        return None
    
# Applications
def api_get_applications(status: str = None) -> list[dict] | None:
    params = {}
    if status and status != "All":
        params["status"] = status
    try:
        response = requests.get(f"{API_URL}/applications", 
                                headers=get_headers(), 
                                params=params, 
                                timeout=10
                                )
        if response.status_code == 200:
            return response.json()
        return []
    except requests.RequestException as e:
        st.error(f"Failed to fetch applications: {e}")
        return []
    
def api_create_application(company: str, position: str, status: str = "Applied", notes: str = "") -> dict | None:
    data = {
        "company": company,
        "position": position,
        "status": status,
        "notes": notes
    }

    try:
        response = requests.post(f"{API_URL}/applications", 
                                 headers=get_headers(), 
                                 json=data, 
                                 timeout=60
                                 )
        if response.status_code == 201:
            return response.json()
        return None
    except requests.RequestException as e:
        st.error(f"Failed to create application: {e}")
        return None
    
def api_update_application(app_id: int, new_status: str, new_notes: str) -> dict | None:
    data = {
        "status": new_status,
        "notes": new_notes
    }
    try:
        response = requests.patch(f"{API_URL}/applications/{app_id}", 
                                headers=get_headers(), 
                                json=data, 
                                timeout=60
                                )
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        st.error(f"Failed to update application: {e}")
        return None
    
def api_delete_application(app_id: int) -> bool:
    try:
        response = requests.delete(f"{API_URL}/applications/{app_id}", 
                                   headers=get_headers(), 
                                   timeout=60
                                   )
        return response.status_code == 204
    except requests.RequestException as e:
        st.error(f"Failed to delete application: {e}")
        return False
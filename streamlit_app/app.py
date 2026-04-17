import streamlit as st
from pages.login import show_login_page
from pages.dashboard import show_dashboard  

# page config - must be the first streamlit call in the app
st.set_page_config(
    page_title="Job Application Tracker", 
    page_icon="📊", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize session state defaults
defaults = {
    "token": None,              # JWT Token
    "user_email": None,         # logged in user's email
    'page': "login",            # default page is login
    'confirm_delete': None      # default delete confirmation state
}
for key, value in defaults.items():  
    if key not in st.session_state: # if the key is not already in session state, initialize it with the default value
        st.session_state[key] = value # this ensures that we don't overwrite existing session state values on page reloads, but we do have all the necessary keys initialized for the app to function properly

# route to correct page based on session state
if st.session_state.token is None:
    show_login_page()
else:
    show_dashboard()
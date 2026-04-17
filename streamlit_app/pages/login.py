import streamlit as st
from api import api_login, api_register

def show_login_page():
    st.markdown("<h1 style='text-align: center;'>Job Application Tracker</h1>", unsafe_allow_html=True)

    # 1. Initialize the view state if it doesn't exist
    if "auth_view" not in st.session_state: # this ensures that we have a default view set when the user first lands on the login page
        st.session_state.auth_view = "login"

    # --- LOGIN VIEW ---
    if st.session_state.auth_view == "login":
        st.subheader("Login")
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Enter your email", key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
            submit = st.form_submit_button("Login", use_container_width=True)

        if submit:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                with st.spinner("Logging in..."):
                    result = api_login(email, password)
                if result:
                    st.session_state.token = result["access_token"]
                    st.session_state.user = {"email": email}
                    st.success("Login successful!")
                    st.rerun() # Refresh to show the dashboard
                else:
                    st.error("Login failed. Please check your credentials.")

        # Button to switch to Register (Outside the form)
        st.write("---")
        if st.button("Don't have an account? Click to Register !!!"):
            st.session_state.auth_view = "register"
            st.rerun()

    # --- REGISTER VIEW ---
    elif st.session_state.auth_view == "register":
        st.subheader("Create New Account")
        with st.form("register_form"):
            email = st.text_input("Email", placeholder="Enter your email", key="register_email")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="register_password")
            submit = st.form_submit_button("Register", use_container_width=True)

        if submit:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                with st.spinner("Registering..."):
                    result = api_register(email, password)
                if result:
                    st.success("Registration successful! Redirecting to login...")
                    # 2. Set view back to login and rerun
                    st.session_state.auth_view = "login"
                    st.rerun()
                else:
                    st.error("Registration failed. Email might already be in use.")

        # Button to switch back to Login
        st.write("---")
        if st.button("Already have an account? Log in"):
            st.session_state.auth_view = "login"
            st.rerun()
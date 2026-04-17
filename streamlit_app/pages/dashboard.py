import streamlit as st
import pandas as pd
from api import api_get_applications, api_create_application, api_update_application, api_delete_application

STATUS_OPTIONS = ["Applied", "Interview", "Offered", "Rejected"]
STATUS_EMOJI = {
    "Applied": "📄",
    "Interview": "💬",
    "Offered": "💰",
    "Rejected": "❌"
}

def show_dashboard():
    st.title("Dashboard")
    st.subheader(f"Welcome, {st.session_state.user['email']}!")
    
    # Form to add new application
    with st.expander("Add New Application"):
        with st.form("add_app_form"):
            company = st.text_input("Company", placeholder="Enter company name")
            position = st.text_input("Position", placeholder="Enter position title")
            status = st.selectbox("Status", STATUS_OPTIONS)
            notes = st.text_area("Notes", placeholder="Additional notes (optional)")
            submit = st.form_submit_button("Add Application", use_container_width=True)
        if submit:
            if not company or not position:
                st.error("Please enter both company and position.")
            else:
                with st.spinner("Adding application..."):
                    new_app = api_create_application(company, position, status, notes)
                if new_app:
                    st.success("Application added successfully!")
                else:
                    st.error("Failed to add application. Please try again.")
    
    # Fetch and display applications
    applications = api_get_applications()
    if applications:
        df = pd.DataFrame(applications)
        df["Status"] = df["status"].apply(lambda x: f"{STATUS_EMOJI.get(x, '')} {x}")
        df_display = df[["company", "position", "Status", "notes"]]
        st.dataframe(df_display, use_container_width=True)
        
        # Edit and delete options
        for idx, app in enumerate(applications):
            col1, col2 = st.columns([1, 0.2])
            with col1:
                st.markdown(f"**{app['company']} - {app['position']}**")
            with col2:
                edit_btn = st.button(f"Edit##{idx}", use_container_width=True)
                delete_btn = st.button(f"Delete##{idx}", use_container_width=True)
            
            if edit_btn:
                with st.expander(f"Edit Application: {app['company']} - {app['position']}"):
                    new_status = st.selectbox("Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(app["status"]))
                    new_notes = st.text_area("Notes", value=app["notes"])
                    update_btn = st.button(f"Update##{idx}", use_container_width=True)
                    if update_btn:
                        with st.spinner("Updating application..."):
                            updated_app = api_update_application(app["id"], new_status, new_notes)
                        if updated_app:
                            st.success("Application updated successfully!") 
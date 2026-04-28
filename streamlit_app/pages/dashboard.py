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
STATUS_COLOR = {
    "Applied":   "#3B82F6",   # blue
    "Interview": "#F59E0B",   # amber
    "Offered":   "#10B981",   # green
    "Rejected":  "#EF4444",   # red
}

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Job Tracker", layout="centered")

# ── Hide sidebar + global styles ───────────────────────────────────────────────
st.markdown("""
<style>
/* Hide sidebar entirely */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* Center the whole app */
.block-container {
    max-width: 860px;
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

/* Gradient header banner */
.header-banner {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #EC4899 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.8rem;
    text-align: center;
    color: white;
}
.header-banner h1 {
    display: flex;
    align-items: center;
    margin: 0 0 0.3rem 0;
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
}
.header-banner p {
    margin: 0;
    font-size: 1rem;
    opacity: 0.88;
}

/* Status badge pills */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    color: white;
}

/* Card rows for each application */
.app-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}
.app-info { flex: 1; }
.app-title {
    font-weight: 700;
    font-size: 1rem;
    color: #F1F5F9;
    margin-bottom: 4px;
}
.app-meta {
    font-size: 0.82rem;
    color: #94A3B8;
}

/* Expander styling */
[data-testid="stExpander"] {
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    background: #0F172A !important;
}

/* Metric cards */
.metric-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    justify-content: center;
}
.metric-card {
    flex: 1;
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.metric-card .num {
    font-size: 1.8rem;
    font-weight: 800;
    line-height: 1;
}
.metric-card .label {
    font-size: 0.78rem;
    color: #94A3B8;
    margin-top: 4px;
}

/* Section headers */
.section-header {
    display: flex;
    align-items: center;      
    font-size: 2rem;
    font-weight: 700;
    color: #CBD5E1;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 1.5rem 0 0.75rem 0;
    border-bottom: 1px solid #334155;
    padding-bottom: 0.5rem;
}

/* Make buttons more colorful */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.15s ease !important;
}
</style>
""", unsafe_allow_html=True)


def show_dashboard():
    user_email = st.session_state.user["email"]

    # ── Header banner ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="header-banner">
        <h1>🎯 Job Tracker</h1>
        <p>Welcome back, <strong>{user_email}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # ── Fetch applications ─────────────────────────────────────────────────────
    applications = api_get_applications() or []

    # ── Stats row ──────────────────────────────────────────────────────────────
    counts = {s: sum(1 for a in applications if a.get("status") == s) for s in STATUS_OPTIONS}
    total  = len(applications)

    cols = st.columns(5)
    metrics = [("Total", total, "#6366F1")] + [
        (s, counts[s], STATUS_COLOR[s]) for s in STATUS_OPTIONS
    ]
    for col, (label, num, color) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="label">{label}</div>
                <div class="num" style="color:{color}; text-align: center;">{num}</div>
                <p></p>
            </div>""", unsafe_allow_html=True)

    # ── Add New Application ────────────────────────────────────────────────────
    st.markdown('<div class="section-header"><p> </p></div>', unsafe_allow_html=True)
    with st.expander("➕ Add New Application", expanded=False):
        with st.form("add_app_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            company  = c1.text_input("Company")
            position = c2.text_input("Position")
            c3, c4 = st.columns(2)
            status = c3.selectbox("Status", STATUS_OPTIONS)
            salary = c4.text_input("Salary", placeholder="optional")
            notes  = st.text_area("Notes", placeholder="Additional notes (optional)", height=80)
            submit = st.form_submit_button("✅ Add Application", use_container_width=True)

        if submit:
            if not company or not position:
                st.error("Please enter both company and position.")
            else:
                with st.spinner("Adding application..."):
                    new_app = api_create_application(company, position, status, notes)
                if new_app:
                    st.success("Application added!")
                    st.rerun()
                else:
                    st.error("Failed to add application. Please try again.")

    # ── Applications table ─────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 Your Applications</div>', unsafe_allow_html=True)
    st.divider()

    if not applications:
        st.info("No applications yet — add your first one above!")
        return

    # Column headers
    hcols = st.columns([2.5, 2, 2, 1.5, 1.2, 0.8, 0.8])
    for col, label in zip(hcols, ["Company", "Position", "Salary", "Status", "Date Applied", "Edit", "Delete"]):
        col.markdown(f"**{label}**")
    st.divider()

    # One row per application
    for idx, app in enumerate(applications):
        status_val = app.get("status", "Applied")
        badge_color = STATUS_COLOR.get(status_val, "#6366F1")
        date_str = app.get("date_applied", "—")[:10] if app.get("date_applied") else "—"

        row = st.columns([2.5, 2, 2, 1.5, 1.2, 0.8, 0.8])
        row[0].markdown(f"{app.get('company', '—')}")
        row[1].markdown(app.get("position", "—"))
        row[2].markdown(app.get("salary", "—"))
        row[3].markdown(
            f'{STATUS_EMOJI.get(status_val,"")} {status_val}</span>',
            unsafe_allow_html=True
        )
        row[4].markdown(date_str)
        edit_btn   = row[5].button("✏️", key=f"edit_{idx}",   help="Edit",   use_container_width=True)
        delete_btn = row[6].button("🗑️", key=f"delete_{idx}", help="Delete", use_container_width=True)

        # ── Edit form (inline expander below the row) ──────────────────────────
        if edit_btn:
            st.session_state[f"editing_{idx}"] = not st.session_state.get(f"editing_{idx}", False)

        if st.session_state.get(f"editing_{idx}", False):
            with st.expander(f"Editing: {app['company']} — {app['position']}", expanded=True):
                with st.form(f"edit_form_{idx}"):
                    new_status = st.selectbox(
                        "Status", STATUS_OPTIONS,
                        index=STATUS_OPTIONS.index(status_val)
                    )
                    new_notes = st.text_area("Notes", value=app.get("notes", ""), height=80)
                    ec1, ec2 = st.columns(2)
                    save_btn   = ec1.form_submit_button("💾 Save",   use_container_width=True)
                    cancel_btn = ec2.form_submit_button("✖ Cancel", use_container_width=True)

                if save_btn:
                    with st.spinner("Updating..."):
                        updated = api_update_application(app["id"], new_status, new_notes)
                    if updated:
                        st.success("Updated!")
                        st.session_state[f"editing_{idx}"] = False
                        st.rerun()
                    else:
                        st.error("Update failed.")
                if cancel_btn:
                    st.session_state[f"editing_{idx}"] = False
                    st.rerun()

        # ── Delete confirmation ────────────────────────────────────────────────
        if delete_btn:
            st.session_state[f"confirm_delete_{idx}"] = True

        if st.session_state.get(f"confirm_delete_{idx}", False):
            st.warning(f"Delete **{app['company']} – {app['position']}**?")
            dc1, dc2 = st.columns(2)
            if dc1.button("Yes, delete", key=f"confirm_yes_{idx}", use_container_width=True):
                with st.spinner("Deleting..."):
                    api_delete_application(app["id"])
                st.session_state[f"confirm_delete_{idx}"] = False
                st.rerun()
            if dc2.button("Cancel", key=f"confirm_no_{idx}", use_container_width=True):
                st.session_state[f"confirm_delete_{idx}"] = False
                st.rerun()

        st.divider()
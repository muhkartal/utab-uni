import streamlit as st
from main_page import main_page
from request_page import request_page
from chart_page import show_charts
from admin import admin_page 
from teacher_page import teacher_page

# Initialize session state for page tracking
if 'selected_page' not in st.session_state:
    st.session_state['selected_page'] = 'Home Page'

def render_navigation():
    st.sidebar.title("Student Answer Evaluation ")  # Sidebar title
    
    # Section: Account
    st.sidebar.markdown("### Account")
    if st.sidebar.button("🔗 Log Out"):  # Log out button
        st.session_state['teacher_info'] = None
        st.rerun()
    
    # Section: Reports
    st.sidebar.markdown("### Reports")

    # Maintain button visibility and update the selected page in session state
    if st.sidebar.button("📊 Home Page"):
        st.session_state['selected_page'] = "Home Page"
    if st.sidebar.button("📄 Request"):
        st.session_state['selected_page'] = "Request"
    if st.sidebar.button("📈 Charts"):
        st.session_state['selected_page'] = "Charts"
    if st.sidebar.button("📚 Exam Portal"):
        st.session_state['selected_page'] = "Portal"

    # Show Admin Page button if the user is 'admin'
    if st.session_state['teacher_info'] and st.session_state['teacher_info'][1] == 'admin':  # Check if the logged-in user is 'admin'
        st.sidebar.markdown("### Admin")
        if st.sidebar.button("🔧 Exam Portal"):
            st.session_state['selected_page'] = "Admin"

def handle_navigation():
    # Create navigation menu
    render_navigation()

    # Show the selected page based on session state
    if st.session_state['selected_page'] == "Home Page":
        main_page()
    elif st.session_state['selected_page'] == "Request":
        request_page()
    elif st.session_state['selected_page'] == "Charts":
        show_charts()
    elif st.session_state['selected_page'] == "Portal":
        teacher_page()  # Call the teacher page
    elif st.session_state['selected_page'] == "Admin":
        admin_page()  # Call the admin page

if __name__ == "__main__":
    handle_navigation()

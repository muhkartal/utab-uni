import streamlit as st
from login_page import login_page
from main_page import main_page
from request_page import request_page
from navigation import handle_navigation
from chart_page import show_charts
from admin import admin_page
from teacher_page import teacher_page

# Check if teacher is logged in
if 'teacher_info' not in st.session_state:
    st.session_state['teacher_info'] = None

# Control flow based on login status
if st.session_state['teacher_info'] is None:
    login_page()  # Show login page if not logged in
else:
    handle_navigation()  # Handle page navigation

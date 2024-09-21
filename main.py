import streamlit as st
from utab.app.login_page import login_page
from utab.app.main_page import main_page
from utab.app.request_page import request_page
from utab.app.navigation import handle_navigation
from utab.app.chart_page import show_charts
from admin import admin_page
from utab.app.teacher_page import teacher_page

# Check if teacher is logged in
if 'teacher_info' not in st.session_state:
    st.session_state['teacher_info'] = None

# Control flow based on login status
if st.session_state['teacher_info'] is None:
    login_page()  # Show login page if not logged in
else:
    handle_navigation()  # Handle page navigation

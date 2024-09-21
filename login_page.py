import streamlit as st
import mysql.connector

def apply_styles():
    st.markdown("""
        <style>
        body {
            background: linear-gradient(135deg, #E8F0F2, #F9F9F9);
            font-family: 'Arial', sans-serif;
        }
        .login-container {
            max-width: 400px;
            margin: auto;
            padding: 50px;
            border-radius: 15px;
            background-color: #ffffff;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        .stButton > button {
            font-size: 16px;
            padding: 12px 40px;
            background-color: #612C28;
            color: white;
            border: none;
            border-radius: 5px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transition: background-color 0.3s ease, transform 0.2s ease;
        }        
        </style>
    """, unsafe_allow_html=True)

# MySQL connection function
def get_connection():
    return mysql.connector.connect(
        host="your_localhost",
        user="your_root",
        password="your_pass",
        database="your_database"
    )

def login_page():
    apply_styles()
    
    with st.container():
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)

        st.title("Teacher Login")
        teacher_name = st.text_input("Teacher Name", max_chars=50, placeholder="Enter your username")
        teacher_pass = st.text_input("Password", type="password", max_chars=50, placeholder="Enter your password")

        if st.button("Login"):
            # Authenticate teacher or admin
            teacher_info = authenticate_teacher(teacher_name, teacher_pass)
            
            if teacher_info:
                st.session_state['teacher_info'] = teacher_info
                if teacher_name == 'admin':  # Check if the logged-in user is 'admin'
                    st.success("Admin login successful! Redirecting to admin page...")
                    st.session_state['selected_page'] = 'Admin'  # Direct to admin page
                    st.rerun()  # Reload the app after successful login
                else:
                    st.success("Login successful! Redirecting...")
                    st.rerun()  # Reload the app after successful login
            else:
                st.error("Invalid login credentials")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Authenticate teacher or admin and retrieve basic information
def authenticate_teacher(teacher_name, teacher_pass):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT teacher_id, teacher_name, faculty_id, dep_id, assigned_file
    FROM teacher 
    WHERE teacher_name = %s AND teacher_pass = %s
    """
    cursor.execute(query, (teacher_name, teacher_pass))
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return result

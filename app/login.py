import streamlit as st
import mysql.connector

# MySQL connection function
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="utab"
    )

# Authenticate teacher and retrieve basic information
def authenticate_teacher(teacher_name, teacher_pass):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT teacher_id, teacher_name, faculty_name, dep_id, assigned_file 
    FROM teacher 
    WHERE teacher_name = %s AND teacher_pass = %s
    """
    cursor.execute(query, (teacher_name, teacher_pass))
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return result

# Set up session state for maintaining login state
if 'teacher_info' not in st.session_state:
    st.session_state['teacher_info'] = None

def apply_styles():
    st.markdown("""
        <style>
        body {
            background: linear-gradient(135deg, #E8F0F2, #F9F9F9);
            font-family: 'Arial', sans-serif;
            color: #333333;
        }
        .login-container {
            max-width: 400px;
            margin: auto;
            padding: 40px;
            border-radius: 15px;
            background-color: #ffffff;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        }
        .stTextInput > div > input {
            font-size: 16px;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #cfcfcf;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        .stTextInput > div > input:focus {
            border-color: #0056b3;
            outline: none;
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
        .stButton > button:hover {
            background-color: #0056b3;
            transform: translateY(-3px);
        }
        .logout-button {
            background-color: #612C28;
            color: white;
            padding: 12px 30px;
            font-size: 16px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            transition: background-color 0.3s ease, box-shadow 0.2s ease;
        }
        .logout-button:hover {
            background-color: #cc0000;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
        }
        .welcome-banner {
            text-align: center;
            padding: 20px;
          
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 24px;
        }
        .info-card {
            padding: 20px;
            border-radius: 10px;
            background-color: #ffffff;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .info-card h3 {
            margin-bottom: 10px;
            color: #333;
        }
        </style>
    """, unsafe_allow_html=True)

# Login page with improved aesthetics
def login_page():
    apply_styles()
    
    with st.container():
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)

        st.title("Teacher Login")
        teacher_name = st.text_input("Teacher Name", max_chars=50, placeholder="Enter your username")
        teacher_pass = st.text_input("Password", type="password", max_chars=50, placeholder="Enter your password")

        if st.button("Login"):
            teacher_info = authenticate_teacher(teacher_name, teacher_pass)
            
            if teacher_info:
                st.session_state['teacher_info'] = teacher_info
                st.success("Login successful! Redirecting...")
                st.rerun()  # Reload the app after successful login
            else:
                st.error("Invalid login credentials")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Main page after successful login with aesthetics
def main_page():
    apply_styles()

    teacher_info = st.session_state['teacher_info']
    teacher_id, teacher_name, faculty_name, dep_id, _ = teacher_info
    
    st.markdown(f"<div class='welcome-banner'><h2>Welcome, {teacher_name}!</h2></div>", unsafe_allow_html=True)

 

    st.markdown(f"""
    <div class='info-card'>
        <h3>Teacher Information</h3>
        <ul>
            <li><strong>Teacher ID:</strong> {teacher_id}</li>
            <li><strong>Faculty ID:</strong> {faculty_name}</li>
            <li><strong>Department ID:</strong> {dep_id}</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

    # Fetch assigned files and exam names from the database
    conn = get_connection()
    cursor = conn.cursor()
    
    # Query to retrieve assigned files from teacher and exam_name from exam
    query = """
    SELECT teacher.assigned_file, exam.exam_name 
    FROM teacher 
    JOIN exam ON teacher.teacher_id = exam.teacher_id 
    WHERE teacher.teacher_id = %s
    """
    cursor.execute(query, (teacher_id,))
    files = cursor.fetchall()

    cursor.close()
    conn.close()

    # Extract files and exam names into a list
    file_options = [(f[0], f[1]) for f in files]  # (assigned_file, exam_name)

    # If there are files, use selectbox to display them
    if file_options:
        selected_file_info = st.selectbox("Select the exam to download the file", file_options, format_func=lambda x: x[1])
        selected_file, exam_name = selected_file_info
        
        st.download_button(
            label="Download Selected File",
            data=selected_file,
            file_name=f"{exam_name}_teacher_{teacher_id}.xls",
            mime="application/vnd.ms-excel"
        )
    else:
        st.warning("No file assigned to you.")

    if st.button("Logout"):
        st.session_state['teacher_info'] = None
        st.rerun()

# Application flow control
if st.session_state['teacher_info'] is None:
    login_page()  # Show login page if not logged in
else:
    main_page()  # Show main page if logged in

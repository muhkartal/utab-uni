import streamlit as st
import mysql.connector

# MySQL connection function
def get_connection():
    return mysql.connector.connect(
        host="your_host",
        user="your_user",
        password="your_password",
        database="your_database"
    )
def apply_styles():
    st.markdown("""
        <style>
        .welcome-banner {
            text-align: center;
            padding: 10px;    
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 24px;
        }
        .info-card {
            padding: 20px;
            border-radius: 10px;
            background-color: #ffffff;box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

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
            <li><strong>Name: :</strong> {teacher_name}</li>
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

   # Add CSS for centering the button
    st.markdown("""
        <style>
        .centered-button {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='centered-button'>", unsafe_allow_html=True)
    
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
    
    st.markdown("</div>", unsafe_allow_html=True)

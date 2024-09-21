import streamlit as st
import pandas as pd
import mysql.connector


def calculate_results(student_data, correct_answers):
    # Calculate correct and wrong answers for each student
    results = []
    
    for student_id, student_name, student_answers in student_data:
        correct_count = sum(1 for i, answer in enumerate(student_answers) if answer == correct_answers[i])
        wrong_count = len(correct_answers) - correct_count
        results.append((student_id, student_name, correct_count, wrong_count))
    
    return results

def display_results(results):
    # Display the results in a DataFrame
    df = pd.DataFrame(results, columns=['Student ID', 'Student Name', 'Correct Answers', 'Wrong Answers'])
    st.dataframe(df)

def get_teacher_data():
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="your_host",
        user="your_user",
        password="your_password",
        database="your_database"
    )
    
    query = "SELECT answer FROM teacher WHERE teacher_id = %s"
    teacher_id = st.text_input("Enter Teacher ID")
    
    if teacher_id:
        cursor = conn.cursor()
        cursor.execute(query, (teacher_id,))
        result = cursor.fetchone()
        
        if result:
            # Decode the byte content from the database
            return result[0].decode('ISO-8859-1')
        else:
            st.error("No data found for the given teacher ID.")
            return None
    return None

def highlight_answers(val, correct_answer):
    if val == correct_answer:
        return 'background-color: #173928 '  # Highlight correct answers
    elif val != '':
        return 'background-color: #612C28'  # Highlight incorrect answers
    return ''  # Leave empty cells unhighlighted


def format_answers_with_highlights(df, correct_answers):
    max_len = max(df['Answers'].str.len().max(), len(correct_answers))  # Dynamically detect max number of answers
    formatted_df = df[['ID', 'Name']].copy()

    for i in range(max_len):
        formatted_df[f'Q{i+1}'] = df['Answers'].apply(lambda x: x[i] if i < len(x) else '')

    # Apply styling for correct/incorrect answers
    styled_df = formatted_df.style.apply(
        lambda row: [
            highlight_answers(row[f'Q{i+1}'], correct_answers[i] if i < len(correct_answers) else '') 
            for i in range(max_len)
        ], 
        axis=1,
        subset=[f'Q{i+1}' for i in range(max_len)]
    )

    return styled_df


def parse_dat_file(dat_content):
    # Parse the .dat content to extract student data and 'cevap' (correct answers)
    lines = dat_content.strip().split('\n')
    student_data = []
    students = []
    correct_answers = None
    
    for line in lines:
        if line.lower().startswith('cevap'):  # Detecting the line with correct answers
            correct_answers = line.split()[1]  # Assuming 'cevap' line is formatted as 'cevap ABCD...'
        else:
            # Assuming the format is: ID Name AnswerString
            parts = line.split()
            if len(parts) >= 3:
                student_id = parts[0]
                student_name = parts[1]
                student_answers = parts[2]
                student_data.append((student_id, student_name, student_answers))

            students.append({
                'ID': student_id,
                'Name': student_name,
                'Answers': student_answers
            })
    
    student_df = pd.DataFrame(students)
    
    return student_df, correct_answers


def teacher_page():
    st.title("Sınav Portalı")
    
    dat_content = get_teacher_data()
    df_students, detected_correct_answers = parse_dat_file(dat_content)

    cols = st.columns(10)
    correct_answers_list = list(detected_correct_answers)
    for i, answer in enumerate(correct_answers_list):
            with cols[i % 10]:
                correct_answers_list[i] = st.text_input(f"Soru {i+1}", value=answer, key=f"answer_{i}")

    correct_answers = "".join(correct_answers_list)
    
    styled_df = format_answers_with_highlights(df_students, correct_answers_list)
    st.write("Öğrenci Cevapları:")
    st.dataframe(styled_df)
    
    if dat_content:
        st.text("Data retrieved successfully!")
        
        # Parse the .dat content into a DataFrame
        student_df, correct_answers = parse_dat_file(dat_content)
        
        # Display the parsed student data
        st.dataframe(student_df)
        
        if correct_answers:
            # Calculate correct and wrong answers for each student
            results = calculate_results(student_df, correct_answers)
            
            # Display results in a DataFrame
            display_results(results)
        else:
            st.error("Correct answers (cevap line) not found in the .dat file.")
    else:
        st.info("Please enter a valid Teacher ID to retrieve data.")

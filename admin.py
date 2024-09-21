import streamlit as st
import mysql.connector
import pandas as pd
import re
from io import BytesIO
import xlsxwriter  # Required for Excel writing

# MySQL connection function
def get_connection():
    return mysql.connector.connect(
        host="your_localhost",
        user="your_root",
        password="your_pass",
        database="your_database"
    )


# Fetch teacher names and IDs from the database
def get_teacher_names():
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT teacher_id, teacher_name FROM teacher"
    cursor.execute(query)
    teachers = cursor.fetchall()
    cursor.close()
    conn.close()
    return teachers

# Function to save .dat file to the 'answer' column
def save_dat_file_to_db(teacher_id, file_content):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Prepare SQL query to update the answer in the teacher table
        query = """
        UPDATE teacher
        SET answer = %s
        WHERE teacher_id = %s
        """
        cursor.execute(query, (file_content, teacher_id))
        conn.commit()
        st.success("File saved to the database successfully!")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()



def upload_files_to_mysql(teacher_id, results_file, exam_name):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Update the result in the teacher table
    query_teacher = "UPDATE teacher SET result = %s WHERE teacher_id = %s"
    cursor.execute(query_teacher, (results_file, teacher_id))
    
    # Update the exam_name in the exam table
    query_exam = "UPDATE exam SET exam_name = %s WHERE teacher_id = %s"
    cursor.execute(query_exam, (exam_name, teacher_id))
    
    conn.commit()
    cursor.close()
    conn.close()
# Function to convert DataFrame to Excel binary format
def dataframe_to_xls(df):
    output = BytesIO()

    # Write the DataFrame to the Excel file in the output buffer
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)  # Writing DataFrame to Excel

    # Get the content of the buffer
    output.seek(0)  # Rewind the buffer
    return output

def parse_dat_file(dat_content):
    students = []
    correct_answers = ""
    
    for line in dat_content.strip().split('\n'):
        if line.lower().startswith('cevap'):  # Detecting the line with correct answers
            correct_answers = line.split()[1]  # Assuming correct answers follow the keyword 'cevap'
        else:
            fields = re.split(r'\s+', line.strip())
            student_id = fields[0]
            student_name = " ".join(fields[1:-1]).strip()  # Combining parts of the name
            answers = fields[-1] if len(fields) > 1 else ""  # Getting the answer string

            students.append({
                'ID': student_id,
                'Name': student_name,
                'Answers': answers
            })
    
    # Convert list of students to a DataFrame
    student_df = pd.DataFrame(students)
    
    # Return the DataFrame and correct answers
    return student_df, correct_answers

def save_to_xls(dataframe, correct_answers, filename='modified_file.xls'):
    # Write to an Excel file
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, sheet_name='Students', index=False)
        
        # Create a separate sheet for correct answers if needed
        correct_df = pd.DataFrame({'Correct Answers': [correct_answers]})
        correct_df.to_excel(writer, sheet_name='Correct Answers', index=False)
        

# Function to calculate student results based on answers
def calculate_results(df, correct_answers):
    results = []
    total_questions = len(correct_answers)

    for _, row in df.iterrows():
        student_result = {
            'ID': row['ID'],
            'Name': row['Name'],
            'Total_Correct': 0,
            'Total_Wrong': 0
        }
        for i in range(total_questions):
            student_answer = row['Answers'][i] if i < len(row['Answers']) else ''
            correct_answer = correct_answers[i] if i < len(correct_answers) else ''
            
            if student_answer == correct_answer:
                student_result['Total_Correct'] += 1
            else:
                student_result['Total_Wrong'] += 1

        results.append(student_result)

    return pd.DataFrame(results)

def get_all_teachers():
    conn = get_connection()  # Use your connection function here
    cursor = conn.cursor()
    query = "SELECT teacher_id, teacher_name FROM teacher"
    cursor.execute(query)
    teachers = cursor.fetchall()
    cursor.close()
    conn.close()
    return teachers

def highlight_answers(val, correct_answer):
    if val == correct_answer:
        return 'background-color: #173928 '  # Highlight correct answers
    elif val != '':
        return 'background-color: #612C28'  # Highlight incorrect answers
    return ''  # Leave empty cells unhighlighted

# Function to highlight answers based on correct answers
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

def read_and_convert_dat_to_xls(dat_file_path, xls_output_path):
    # Initialize empty lists to store parsed data
    ids = []
    names = []
    student_answers = []
    correct_answers = []
    
    # Open and read the .dat file
    with open(dat_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Iterate through each line to process the content
    for line in lines:
        # Remove any leading/trailing whitespace
        line = line.strip()

        if line.startswith('cevap'):
            # Extract correct answers from 'cevap' line (the part after the word 'cevap')
            correct_answers = list(line.split()[1])
        else:
            # For students, the first 11 characters are ID, then the name, and finally the answers
            student_id = line[:11].strip()  # First 11 characters
            name_and_answers = line[11:].strip()  # Rest part
            name_parts = name_and_answers.split()  # Split by whitespace
            
            name = ' '.join(name_parts[:-1])  # Everything except last part is name
            answers = list(name_parts[-1])  # Last part is the answer string
            
            # Append the data to respective lists
            ids.append(student_id)
            names.append(name)
            student_answers.append(answers)

    # Create a DataFrame to store the parsed data
    data = {
        'ID': ids,
        'Name': names,
        'Answers': [''.join(ans) for ans in student_answers]  # Convert list of answers back to string
    }

    df = pd.DataFrame(data)

    # Add correct answers as the header row
    df.loc[-1] = ['Correct', 'Answers', ''.join(correct_answers)]
    df.index = df.index + 1  # Shift index for correct answers
    df = df.sort_index()  # Sort index so that 'Correct Answers' is at the top

    # Save DataFrame as an .xls file
    df.to_excel(xls_output_path, index=False)

def admin_page():
    if 'results_df' not in st.session_state:
        st.session_state.results_df = None
        st.session_state.xls_file = None
        st.session_state.dat_xls_file = None

    st.title("Haliç Üniversitesi Sınav Portalı")

    uploaded_file = st.file_uploader("Lütfen .dat dosyasını yükleyin", type="dat")

    if uploaded_file:
        try:
            dat_content = uploaded_file.read().decode('ISO-8859-1')
            df_students, detected_correct_answers = parse_dat_file(dat_content)
            st.success("Dosya başarıyla yüklendi ve analiz edildi!")
        except Exception as e:
            st.error(f"Dosya işleme hatası: {e}")
            st.stop()

        st.session_state.dat_xls_file = dataframe_to_xls(df_students)

        cols = st.columns(10)
        correct_answers_list = list(detected_correct_answers)
        for i, answer in enumerate(correct_answers_list):
            with cols[i % 10]:
                correct_answers_list[i] = st.text_input(f"Soru {i+1}", value=answer, key=f"answer_{i}")

        correct_answers = "".join(correct_answers_list)

        styled_df = df_students.style.applymap(lambda val: 'background-color: lightgreen' if val in correct_answers else '')
        st.write("Öğrenci Cevapları:")
        st.dataframe(styled_df)

        if st.button("Sonuçları Hesapla"):
            st.session_state.results_df = calculate_results(df_students, correct_answers)
            st.session_state.xls_file = dataframe_to_xls(st.session_state.results_df)

            st.write("Sonuçlar:")
            st.dataframe(st.session_state.results_df)

            st.download_button(
                label="Sonuçları İndir",
                data=st.session_state.xls_file,
                file_name="student_results.xls",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    if st.session_state.dat_xls_file is not None and st.session_state.results_df is not None:
        teachers = get_teacher_names()

        if teachers:
            teacher_option = st.selectbox("Öğretmen Seçin", [name for _, name in teachers])
            selected_teacher_id = [id for id, name in teachers if name == teacher_option][0]

            exam_name = 'modified_file.xls'

            if st.button("Sonuçları Yükle ve Öğretmene Ata"):
                try:
                    upload_files_to_mysql(selected_teacher_id, st.session_state.dat_xls_file.getvalue(), exam_name)
                    st.success(f"Sonuçlar {teacher_option} öğretmenine başarıyla yüklendi.")
                except Exception as e:
                    st.error(f"Sonuçlar yüklenirken bir hata oluştu: {str(e)}")
        else:
            st.warning("Sistemde öğretmen bulunamadı.")

    st.title("Upload .dat File to Save in Database")

    teachers = get_teacher_names()
    teacher_option = st.selectbox("Select Teacher", [name for _, name in teachers])
    selected_teacher_id = [id for id, name in teachers if name == teacher_option][0]

    uploaded_file = st.file_uploader("Choose a .dat file", type="dat")

    if uploaded_file is not None:
        file_content = uploaded_file.read().decode('ISO-8859-1')

        if st.button("Save to Database"):
            save_dat_file_to_db(selected_teacher_id, file_content)
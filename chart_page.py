import streamlit as st
import mysql.connector
import pandas as pd
import io
import matplotlib.pyplot as plt

# Connect to MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host="your_localhost",
        user="your_root",
        password="your_pass",
        database="your_database"
    )

def get_teacher_result(teacher_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "SELECT result FROM teacher WHERE teacher_id = %s"
        cursor.execute(query, (teacher_id,))
        result = cursor.fetchone()

        if result and result[0]:
            # Convert LONGBLOB to Excel
            xls_data = result[0]
            excel_bytes = io.BytesIO(xls_data)
            
            # Try loading the data into a DataFrame
            try:
                df = pd.read_excel(excel_bytes, header=None)  # No headers assumed
                return df
            except Exception as e:
                st.error(f"Error loading Excel data for teacher {teacher_id}: {e}")
                return None
        else:
            st.warning(f"No data found for Teacher ID: {teacher_id}")
            return None
    except Exception as e:
        st.error(f"Database query error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# Function to get correct/incorrect answer marks
def get_answer_marks(val, correct_answer):
    if val == correct_answer:
        return '✔️'  # Correct answer symbol
    elif val != '':
        return '❌'  # Incorrect answer symbol
    return ''  # Empty cells

# Function to format answers with symbols
def format_answers_with_marks(df, correct_answers):
    max_len = len(correct_answers)  # Number of questions
    formatted_df = pd.DataFrame()
    
    # Extract and format answers
    for i in range(max_len):
        formatted_df[f'Q{i+1}'] = df[df.columns[-1]].apply(lambda x: get_answer_marks(x[i], correct_answers[i]) if i < len(x) else '')

    return formatted_df

def display_per_question_distribution(df):
    # Assuming the first column is the question identifier and the last column is the answers
    questions_column = df.columns[0]
    answers_column = df.columns[-1]
    
    # Initialize a dictionary to store percentages for each question
    question_percentages = {}

    # Process each question
    for question_id in df[questions_column].unique():
        # Filter rows for the current question
        question_df = df[df[questions_column] == question_id]
        
        # Count occurrences of each answer choice (A, B, C, D, E)
        answer_choices = ['A', 'B', 'C', 'D', 'E']
        answer_counts = {choice: 0 for choice in answer_choices}

        for answer_string in question_df[answers_column]:
            if isinstance(answer_string, str):  # Ensure the value is a string
                for answer in answer_string:
                    if answer in answer_counts:
                        answer_counts[answer] += 1
        
        # Convert counts to percentages
        total_answers = sum(answer_counts.values())
        if total_answers > 0:
            answer_percentages = {choice: (count / total_answers) * 100 for choice, count in answer_counts.items()}
        else:
            answer_percentages = {choice: 0 for choice in answer_choices}
        
        question_percentages[question_id] = answer_percentages

    # Convert question_percentages to a DataFrame
    question_percentages_df = pd.DataFrame(question_percentages).T
    question_percentages_df.index.name = 'Question ID'
    
    # Display the DataFrame in Streamlit
    st.write("Percentage Distribution of Answers by Question:")
    st.write(question_percentages_df)

   
# Analyze and display the distribution of answers
def analyze_answers_distribution(df):
    # Assuming the last column in each row contains the answer string
    answer_column = df.columns[-1]

    # Count occurrences of each answer choice (A, B, C, D, E)
    answer_choices = ['A', 'B', 'C', 'D', 'E']
    answer_counts = {choice: 0 for choice in answer_choices}

    for answer_string in df[answer_column]:
        if isinstance(answer_string, str):  # Make sure the value is a string
            for answer in answer_string:
                if answer in answer_counts:
                    answer_counts[answer] += 1

    # Convert to a pandas Series for easier charting
    answer_counts_series = pd.Series(answer_counts)
    
    # Plot the distribution as a bar chart
    st.write("Bar Chart of Answer Distribution:")
    st.bar_chart(answer_counts_series)

def show_charts():
    st.title("Teacher Result Data Visualization")

    # Select teacher by ID
    teacher_id = st.number_input("Enter Teacher ID", min_value=1, step=1)
    correct_answers = 'CDAECBABBDABAEBBCCEEADDCBECCCADABCBDEBCEDACCABEBDE'  # Example correct answers
    if st.button("Load Data"):
        # Load and display data
        df = get_teacher_result(teacher_id)
        if df is not None:
            st.write("Showing the first few rows of data:")
            st.dataframe(df.head())

            # Automatically analyze and visualize answer distribution
            analyze_answers_distribution(df)

            formatted_df = format_answers_with_marks(df, correct_answers)
            
            # Display the DataFrame with answer marks
            st.write("Correct and Incorrect Answers Marked:")
            st.dataframe(formatted_df)
              # Display per-question distribution
            display_per_question_distribution(df)


if __name__ == "__main__":
    show_charts()

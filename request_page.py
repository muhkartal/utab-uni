import streamlit as st

def apply_styles():
    st.markdown("""
        <style>
        .request-form {
            max-width: 500px;
            margin: auto;
        }
        </style>
    """, unsafe_allow_html=True)

def request_page():
    apply_styles()
    
    st.markdown("<h2>Submit a Request</h2>", unsafe_allow_html=True)

    # Request form
    with st.form(key="request_form"):
        request_subject = st.text_input("Subject", max_chars=100, placeholder="Enter the subject of your request")
        request_description = st.text_area("Description", placeholder="Enter the details of your request")

        # Submit button
        submit_button = st.form_submit_button("Submit Request")

        if submit_button:
            if request_subject and request_description:
                # You can add logic to save the request to a database here
                st.success("Your request has been submitted successfully!")
            else:
                st.error("Please fill out both the subject and description before submitting.")

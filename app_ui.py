import streamlit as st
import requests
import json

# API URL (assuming the Flask app is running locally)
API_URL = "http://127.0.0.1:5000/ask"

# Title for the web app
st.title("AskDB Ai Powered SQL Query Assistant")

# Textbox for user to input their question
question = st.text_input("Ask a question about the employee data:")

# Submit button to trigger the query
if st.button("Submit Query"):
    if question:
        # Send a POST request to the Flask API
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, data=json.dumps({"question": question}))

        if response.status_code == 200:
            data = response.json()
            st.write("Question: ", data["question"])
            st.write("Answer: ", data["answer"])
        else:
            st.write(f"Error: {response.status_code} - {response.text}")
    else:
        st.write("Please enter a question.")

import streamlit as st
import requests
import json
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# API URL (assuming the Flask app is running locally)
API_URL = "http://127.0.0.1:5000/ask"
DB_PATH = "Ecommerce.db"  # Ensure the correct path to the database

# Function to get the database schema
def fetch_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    schema_info = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        schema_info[table_name] = [{"Column Name": col[1], "Data Type": col[2]} for col in columns]
    
    conn.close()
    return schema_info

# Fetch schema before UI loads
schema_data = fetch_schema()

# Title for the web app
st.title("AskDB AI Powered SQL Query Assistant")

# Display database schema
st.subheader("📌 Database Schema Overview")
for table_name, columns in schema_data.items():
    st.write(f"**Table: {table_name}**")
    df_schema = pd.DataFrame(columns)
    st.dataframe(df_schema)

# Textbox for user to input their question
st.subheader("🔍 Ask a Question")
question = st.text_input("Ask a question about the database:")

# Function to check if the user wants a chart
def is_chart_request(question):
    chart_keywords = ["chart", "plot", "graph", "visualize", "draw"]
    return any(keyword in question.lower() for keyword in chart_keywords)

# Function to generate and display a chart
def generate_plot(df, question):
    # Ensure numeric columns are used for plotting
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")  # Convert only numeric columns

    fig, ax = plt.subplots(figsize=(8, 5))

    # Auto-detect numerical and categorical columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()

    if len(numeric_cols) < 1:
        st.warning("No numeric data available for plotting.")
        return None

    if "line chart" in question.lower() and len(numeric_cols) >= 2:
        ax.plot(df[numeric_cols[0]], df[numeric_cols[1]], marker='o', linestyle='-')
        ax.set_xlabel(numeric_cols[0])
        ax.set_ylabel(numeric_cols[1])
        ax.set_title("Line Chart")
        ax.grid(True)

    elif "bar chart" in question.lower() and len(categorical_cols) > 0 and len(numeric_cols) > 0:
        df.groupby(categorical_cols[0])[numeric_cols[0]].mean().plot(kind="bar", ax=ax, color="blue")
        ax.set_xlabel(categorical_cols[0])
        ax.set_ylabel(numeric_cols[0])
        ax.set_title("Bar Chart")

    elif "scatter plot" in question.lower() and len(numeric_cols) >= 2:
        df.plot(kind="scatter", x=numeric_cols[0], y=numeric_cols[1], ax=ax, color="red")
        ax.set_xlabel(numeric_cols[0])
        ax.set_ylabel(numeric_cols[1])
        ax.set_title("Scatter Plot")

    elif "pie chart" in question.lower() and len(categorical_cols) > 0 and len(numeric_cols) > 0:
        df.groupby(categorical_cols[0])[numeric_cols[0]].sum().plot(kind="pie", autopct="%1.1f%%", startangle=90, ax=ax)
        ax.set_ylabel("")
        ax.set_title("Pie Chart")

    else:
        st.warning("Could not generate a valid plot for the given query.")
        return None

    return fig

# Submit button to trigger the query
if st.button("Submit Query"):
    if question:
        # Send a POST request to the Flask API
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, data=json.dumps({"question": question}))

        if response.status_code == 200:
            data = response.json()
            st.write("### Question:", data["question"])
            
            # Display the generated SQL query
            if "sql_query" in data:
                st.code(data["sql_query"], language="sql")  # Show SQL query in a formatted block
            
            # Process the result
            if "actual_result" in data and isinstance(data["actual_result"], list) and len(data["actual_result"]) > 0:
                df = pd.DataFrame(data["actual_result"])  # Convert JSON to DataFrame
                
                if is_chart_request(question):
                    st.write("### Visualization:")
                    
                    # Generate and display the chart
                    fig = generate_plot(df, question)
                    if fig:
                        st.pyplot(fig)
                    else:
                        st.warning("No valid numerical data available for plotting.")
                
                else:
                    # Display results as a table if no chart is requested
                    st.write("### Query Result:")
                    st.dataframe(df)

            else:
                st.warning("No results found for the given query.")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    else:
        st.warning("Please enter a question.")

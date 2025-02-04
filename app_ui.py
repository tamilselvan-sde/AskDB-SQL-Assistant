import streamlit as st
import requests
import json
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import time  

# API URL (assuming the Flask app is running locally)
API_URL = "http://127.0.0.1:5000/ask"
DB_PATH = "Ecommerce.db"  

# Initialize session state for history
if "history" not in st.session_state:
    st.session_state.history = []

# Function to fetch all table names
def fetch_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    conn.close()
    return tables

# Function to fetch the schema of a specific table
def fetch_table_schema(table_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    schema = [{"Column Name": col[1], "Data Type": col[2]} for col in cursor.fetchall()]
    conn.close()
    return schema

st.title("AskDB AI Powered SQL Query Assistant")

# Section: Show all tables in the database
st.subheader("📋 Available Tables in Database")
tables = fetch_tables()
selected_table = st.selectbox("Select a table to view its schema:", tables)

if selected_table:
    st.subheader(f"📌 Schema of Table: {selected_table}")

    schema_data = fetch_table_schema(selected_table)
    if schema_data:
        df_schema = pd.DataFrame(schema_data)
        if not df_schema.empty:
            df_transposed = df_schema.T  # Transpose the table
            df_transposed.columns = df_transposed.iloc[0]  # Set column names
            df_transposed = df_transposed[1:]  # Remove the redundant first row

            # Display transposed schema table
            st.table(df_transposed)
        else:
            st.warning(f"No schema found for table: {selected_table}")
    else:
        st.warning(f"No schema found for table: {selected_table}")

# User input for database queries
st.subheader("🔍 Ask a Question")

# Display dropdown with last 5 prompts
selected_history_prompt = st.selectbox("History (Last 5 Prompts):", [""] + st.session_state.history[::-1])

# Use selected history prompt as input
question = st.text_input("Ask a question about the database:", value=selected_history_prompt)

# Function to detect chart requests
def is_chart_request(question):
    chart_keywords = ["chart", "plot", "graph", "visualize", "draw"]
    return any(keyword in question.lower() for keyword in chart_keywords)

# Function to determine chart type from question
def determine_chart_type(question):
    if "line" in question.lower():
        return "line"
    elif "bar" in question.lower():
        return "bar"
    elif "scatter" in question.lower():
        return "scatter"
    elif "pie" in question.lower():
        return "pie"
    return None

# Function to generate appropriate chart
def generate_plot(df, chart_type):
    if df.empty:
        st.warning("No data available for visualization.")
        return
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()

    fig, ax = plt.subplots(figsize=(8, 5))

    if chart_type == "pie" and categorical_cols and numeric_cols:
        df.groupby(categorical_cols[0])[numeric_cols[0]].sum().plot(kind="pie", autopct="%1.1f%%", startangle=90, ax=ax)
        ax.set_ylabel("")
        ax.set_title("Pie Chart")
    
    elif chart_type == "bar" and categorical_cols and numeric_cols:
        df.groupby(categorical_cols[0])[numeric_cols[0]].mean().plot(kind="bar", ax=ax)
        ax.set_xlabel(categorical_cols[0])
        ax.set_ylabel(numeric_cols[0])
        ax.set_title("Bar Chart")
    
    elif chart_type == "line" and len(numeric_cols) >= 2:
        df.plot(x=numeric_cols[0], y=numeric_cols[1], kind="line", marker='o', ax=ax)
        ax.set_xlabel(numeric_cols[0])
        ax.set_ylabel(numeric_cols[1])
        ax.set_title("Line Chart")
    
    elif chart_type == "scatter" and len(numeric_cols) >= 2:
        df.plot(kind="scatter", x=numeric_cols[0], y=numeric_cols[1], ax=ax, color="red")
        ax.set_xlabel(numeric_cols[0])
        ax.set_ylabel(numeric_cols[1])
        ax.set_title("Scatter Plot")
    
    else:
        st.warning(f"No suitable data available for {chart_type} chart.")
        return
    
    st.pyplot(fig)

# Submit query and execute it
if st.button("Submit Query"):
    if question:
        # Store the latest prompt in history (keep last 5)
        if question not in st.session_state.history:
            st.session_state.history.append(question)
            if len(st.session_state.history) > 5:
                st.session_state.history.pop(0)

        ui_start_time = time.time()

        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, data=json.dumps({"question": question}))
        ui_execution_time = (time.time() - ui_start_time) * 1000  

        if response.status_code == 200:
            data = response.json()
            st.write("### Question:", data["question"])

            if "execution_time_ms" in data:
                st.write(f"⚡ **Backend Query Execution Time:** {data['execution_time_ms']} ms")

            st.write(f"🖥 **Total UI Execution Time:** {round(ui_execution_time, 2)} ms")

            if "explanation" in data:
                st.write(f"**📝 Explanation:** {data['explanation']}")

            if "sql_query" in data:
                st.code(data["sql_query"], language="sql")  

            if "actual_result" in data and isinstance(data["actual_result"], list) and len(data["actual_result"]) > 0:
                df = pd.DataFrame(data["actual_result"])  

                if is_chart_request(question):
                    chart_type = determine_chart_type(question)
                    if chart_type:
                        st.write(f"### Visualization ({chart_type.capitalize()} Chart)")
                        generate_plot(df, chart_type)
                else:
                    st.write("### Query Result:")
                    st.dataframe(df)
            else:
                st.warning("No results found.")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    else:
        st.warning("Please enter a question.")

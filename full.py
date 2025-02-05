import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from groq import Groq

# Hardcoded Groq API Key
GROQ_API_KEY = "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"
 # <-- Replace with your actual API key
import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from groq import Groq
import re

# Hardcoded Groq API Key
GROQ_API_KEY = "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"

# Database Path
DB_PATH = "Ecommerce.db"

# Initialize Groq Client
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "query_results" not in st.session_state:
    st.session_state.query_results = {}

# Fetch all tables from the database
def fetch_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    conn.close()
    return tables

# Fetch schema for a specific table
def fetch_table_schema(table_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    schema = pd.DataFrame(cursor.fetchall(), columns=['ID', 'Column Name', 'Data Type', 'Not Null', 'Default', 'PK'])
    conn.close()
    return schema[['Column Name', 'Data Type']]

# Function to clean AI-generated SQL query
def clean_sql_query(generated_sql):
    """Extracts only the SQL query from AI-generated output."""
    match = re.search(r"(SELECT .*?;)", generated_sql, re.DOTALL | re.IGNORECASE)
    return match.group(1) if match else "INVALID SQL"

# Function to generate SQL query using AI
def generate_sql_query(question):
    tables = fetch_tables()
    schema_info = {table: fetch_table_schema(table)['Column Name'].tolist() for table in tables}

    schema_text = "\n".join([f"Table: {table}, Columns: {', '.join(columns)}" for table, columns in schema_info.items()])
    prompt = f"""
    You are an SQL expert. Based on the following database schema, generate an optimized SQL query.
    {schema_text}
    User's question: "{question}"
    Ensure the query is valid for SQLite.
    """
    
    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=500,
            top_p=1
        )
        return clean_sql_query(response.choices[0].message.content.strip())
    except Exception as e:
        st.error(f"Error generating SQL: {e}")
        return "INVALID SQL"

# Execute SQL query
def execute_query(sql_query):
    if not sql_query.strip().upper().startswith("SELECT"):
        st.error("❌ Only SELECT queries are allowed!")
        return pd.DataFrame()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        data = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description] if cursor.description else []
        conn.close()
        return pd.DataFrame(data, columns=column_names)
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return pd.DataFrame()

# Generate chart
def generate_plot(df):
    if df.empty or df.select_dtypes(include=['number']).empty:
        st.warning("⚠️ No numeric data available for visualization.")
        return

    st.subheader("📊 Data Visualization")
    fig, ax = plt.subplots()
    df.plot(kind="bar", ax=ax)
    st.pyplot(fig)

# Sidebar Navigation
with st.sidebar:
    selected = option_menu(
        "AskDB",
        ["📝 Ask Questions", "📚 DB Info", "📜 Query History"],
        icons=['💬', '📚', '📜'],
        menu_icon="📋",
        default_index=0
    )

# Tab: Ask Questions
if selected == "📝 Ask Questions":
    st.title("AI Powered SQL Query Assistant 🎉")
    st.markdown('<p class="header">🔍 Ask a Question in Natural Language</p>', unsafe_allow_html=True)

    question = st.text_area("Enter your question about the database:")
    
    if st.button("Generate & Run Query 🚀"):
        if question:
            sql_query = generate_sql_query(question)
            st.markdown("### AI-Generated SQL Query:")
            st.code(sql_query, language="sql")

            if "INVALID SQL" in sql_query:
                st.error("🚨 AI-generated query is invalid. Please refine your input.")
            else:
                df = execute_query(sql_query)
                st.dataframe(df)
                generate_plot(df)

# Tab: DB Info
elif selected == "📚 DB Info":
    st.title("📚 Database Information")
    st.markdown('<p class="header">📚 View Database Schema</p>', unsafe_allow_html=True)
    
    tables = fetch_tables()
    
    if tables:
        table_name = st.selectbox("Select a table:", tables)
        if table_name:
            schema = fetch_table_schema(table_name)
            st.markdown(f'<p class="subheader">Schema for Table: `{table_name}`</p>', unsafe_allow_html=True)
            st.dataframe(schema)
    else:
        st.info("⚠️ No tables found in the database.")

# Tab: Query History
elif selected == "📜 Query History":
    st.title("📜 Query History")
    st.markdown('<p class="header">📖 Last 5 Queries</p>', unsafe_allow_html=True)

    if st.session_state.history:
        for i, query in enumerate(st.session_state.history[::-1]):
            with st.expander(f"Query {i+1}: {query}"):
                df = execute_query(query)
                st.dataframe(df)
                generate_plot(df)
    else:
        st.info("⚠️ No query history available yet.")

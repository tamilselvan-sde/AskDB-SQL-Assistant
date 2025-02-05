import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu

# Database Path
DB_PATH = "Ecommerce.db"

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "query_results" not in st.session_state:
    st.session_state.query_results = {}

# Custom CSS for styling
st.markdown("""
<style>
    .header {
        font-size: 24px;
        font-weight: bold;
        color: #4CAF50;
        margin-bottom: 10px;
    }
    .subheader {
        font-size: 20px;
        font-weight: bold;
        color: #FF9800;
        margin-bottom: 10px;
    }
    .info-box {
        background-color: #F5F5F5;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .button-style {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

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

# Execute SQL query and return DataFrame
def execute_query(sql_query):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        data = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description] if cursor.description else []
        conn.close()
        df = pd.DataFrame(data, columns=column_names)
        return df
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return pd.DataFrame()

# Generate a plot based on data
def generate_plot(df, question):
    if df.empty or df.select_dtypes(include=['number']).empty:
        st.warning("⚠️ No numeric data available for visualization.")
        return

    st.subheader("📊 Data Visualization")
    fig, ax = plt.subplots()
    df.plot(kind="bar", ax=ax)
    st.pyplot(fig)

# Sidebar navigation menu
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
    st.markdown('<p class="header">🔍 Ask a SQL Query</p>', unsafe_allow_html=True)
    
    question = st.text_area("Enter your SQL query below:")
    
    if st.button("Submit Query 🚀"):
        if question:
            # Store query history
            if question not in st.session_state.history:
                st.session_state.history.append(question)
                if len(st.session_state.history) > 5:
                    st.session_state.history.pop(0)

            # Execute and display results
            df = execute_query(question)
            st.markdown('<p class="subheader">Query Results:</p>', unsafe_allow_html=True)
            st.dataframe(df)
            generate_plot(df, question)

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
                generate_plot(df, query)
    else:
        st.info("⚠️ No query history available yet.")

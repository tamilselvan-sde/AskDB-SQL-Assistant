import streamlit as st
import pandas as pd
import sqlite3
import requests
import json
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu

# API URL
API_URL = "http://127.0.0.1:5000/ask"
DB_PATH = "Ecommerce.db"

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "rerun_query" not in st.session_state:
    st.session_state.rerun_query = None
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

# Fetch all tables
def fetch_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    conn.close()
    return tables

# Fetch table schema
def fetch_table_schema(table_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    schema = pd.DataFrame(cursor.fetchall(), columns=['ID', 'Column Name', 'Data Type', 'Not Null', 'Default', 'PK'])
    conn.close()
    return schema[['Column Name', 'Data Type']]

# Fetch statistical analysis
def fetch_statistical_analysis(table_name):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    numeric_df = df.select_dtypes(include=['number'])
    if not numeric_df.empty:
        stats = numeric_df.describe().T[['mean', '50%', 'std']]
        stats['variance'] = numeric_df.var()
        return stats.rename(columns={'50%': 'median'})
    else:
        return pd.DataFrame(columns=['mean', 'median', 'std', 'variance'])

# Determine chart type based on question
def determine_chart_type(question):
    if "pie" in question.lower():
        return "pie"
    elif "bar" in question.lower():
        return "bar"
    elif "line" in question.lower():
        return "line"
    elif "scatter" in question.lower():
        return "scatter"
    return None

# Generate appropriate chart
def generate_plot(df, question):
    if df.empty or df.select_dtypes(include=['number']).empty:
        st.warning("⚠️ No numeric data available for visualization.")
        return
    
    chart_type = determine_chart_type(question)
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()
    
    if chart_type and numeric_cols:
        st.subheader(f"📊 {chart_type.capitalize()} Chart")
        fig, ax = plt.subplots()
        
        if chart_type == "pie" and categorical_cols:
            df.groupby(categorical_cols[0])[numeric_cols[0]].sum().plot.pie(autopct="%1.1f%%", ax=ax)
        elif chart_type == "bar" and categorical_cols:
            df.groupby(categorical_cols[0])[numeric_cols[0]].mean().plot(kind="bar", ax=ax)
        elif chart_type == "line" and len(numeric_cols) >= 2:
            df.plot(x=numeric_cols[0], y=numeric_cols[1], kind="line", ax=ax)
        elif chart_type == "scatter" and len(numeric_cols) >= 2:
            df.plot(kind="scatter", x=numeric_cols[0], y=numeric_cols[1], ax=ax)
        else:
            st.warning(f"⚠️ Insufficient data for {chart_type} chart.")
            return
        
        st.pyplot(fig)

# Execute query and store results
def execute_query(question):
    try:
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, data=json.dumps({"question": question}))
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data.get("actual_result", []))
            st.session_state.query_results[question] = {
                "summary": data.get("explanation", "No summary available"),
                "sql_query": data.get("sql_query", "N/A"),
                "execution_time": data.get("execution_time_ms", "N/A"),
                "dataframe": df
            }
            return st.session_state.query_results[question]
        else:
            st.error("❌ Error fetching response")
            return None
    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
        return None

# Sidebar Navigation
with st.sidebar:
    selected = option_menu(
        "AskDB",
        ["📝 Ask Questions", "📚 DB Info", "📜 Query History", "📊 Statistical Analysis"],
        icons=['💬', '📚', '📜', '📊'],
        menu_icon="📋",
        default_index=0,
        styles={
            "container": {"padding": "5px"},
            "icon": {"color": "#4CAF50", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#4CAF50"},
        }
    )

# Tab: Ask Questions
if selected == "📝 Ask Questions" or st.session_state.rerun_query:
    st.title("AI Powered SQL Query Assistant 🎉")  # Title for this tab
    st.markdown('<p class="header">🔍 Ask a Question</p>', unsafe_allow_html=True)
    question = st.text_input("Enter your question about the database:", value=st.session_state.rerun_query if st.session_state.rerun_query else "")
    
    # If rerun_query is set, execute the query automatically
    if st.session_state.rerun_query:
        question = st.session_state.rerun_query
        st.session_state.rerun_query = None  # Clear rerun_query after loading
        result = execute_query(question)
        if result:
            st.markdown('<p class="subheader">Query Summary:</p>', unsafe_allow_html=True)
            st.info(result["summary"])
            st.markdown('<p class="subheader">SQL Query:</p>', unsafe_allow_html=True)
            st.code(result["sql_query"], language="sql")
            st.markdown('<p class="subheader">Execution Time:</p>', unsafe_allow_html=True)
            st.success(f"{result['execution_time']} ms")
            st.markdown('<p class="subheader">Results:</p>', unsafe_allow_html=True)
            st.dataframe(result["dataframe"])
            generate_plot(result["dataframe"], question)
    
    if st.button("Submit Query 🚀", key="submit_query", help="Click to submit your query"):
        if question:
            if question not in st.session_state.history:
                st.session_state.history.append(question)
                if len(st.session_state.history) > 5:
                    st.session_state.history.pop(0)
            result = execute_query(question)
            if result:
                st.markdown('<p class="subheader">Query Summary:</p>', unsafe_allow_html=True)
                st.info(result["summary"])
                st.markdown('<p class="subheader">SQL Query:</p>', unsafe_allow_html=True)
                st.code(result["sql_query"], language="sql")
                st.markdown('<p class="subheader">Execution Time:</p>', unsafe_allow_html=True)
                st.success(f"{result['execution_time']} ms")
                st.markdown('<p class="subheader">Results:</p>', unsafe_allow_html=True)
                st.dataframe(result["dataframe"])
                generate_plot(result["dataframe"], question)

# Tab: DB Info
elif selected == "📚 DB Info":
    st.title("📚 Database Information")  # Title for this tab
    st.markdown('<p class="header">📚 Database Information</p>', unsafe_allow_html=True)
    tables = fetch_tables()
    if tables:
        table_name = st.selectbox("Select a table to view its schema:", tables)
        if table_name:
            schema = fetch_table_schema(table_name)
            st.markdown(f'<p class="subheader">Schema for Table: `{table_name}`</p>', unsafe_allow_html=True)
            st.dataframe(schema)
    else:
        st.info("⚠️ No tables found in the database.")

# Tab: Query History
elif selected == "📜 Query History":
    st.title("📜 Query History")  # Title for this tab
    st.markdown('<p class="header">📖 Last 5 Queries</p>', unsafe_allow_html=True)
    if st.session_state.history:
        for i, query in enumerate(st.session_state.history[::-1]):
            with st.expander(f"Query {i+1}: {query}"):
                if query in st.session_state.query_results:
                    result = st.session_state.query_results[query]
                    st.markdown('<p class="subheader">Query Summary:</p>', unsafe_allow_html=True)
                    st.info(result["summary"])
                    st.markdown('<p class="subheader">SQL Query:</p>', unsafe_allow_html=True)
                    st.code(result["sql_query"], language="sql")
                    st.markdown('<p class="subheader">Execution Time:</p>', unsafe_allow_html=True)
                    st.success(f"{result['execution_time']} ms")
                    st.markdown('<p class="subheader">Results:</p>', unsafe_allow_html=True)
                    st.dataframe(result["dataframe"])
                    generate_plot(result["dataframe"], query)
                if st.button(f"Run Query {i+1} 🚀", key=f"run_query_{i}"):
                    st.session_state.rerun_query = query  # Set rerun_query to the selected query
                    st.rerun()  # Trigger a rerun to execute the query in the "Ask Questions" tab
    else:
        st.info("⚠️ No query history available yet.")

# Tab: Statistical Analysis
elif selected == "📊 Statistical Analysis":
    st.title("📊 Statistical Analysis")  # Title for this tab
    st.markdown('<p class="header">📊 Statistical Analysis</p>', unsafe_allow_html=True)
    tables = fetch_tables()
    if tables:
        table_name = st.selectbox("Select a table for statistical analysis:", tables)
        if table_name:
            stats = fetch_statistical_analysis(table_name)
            if not stats.empty:
                st.markdown(f'<p class="subheader">Statistical Analysis for Table: `{table_name}`</p>', unsafe_allow_html=True)
                st.dataframe(stats)
            else:
                st.info("⚠️ No numeric columns found in the selected table.")
    else:
        st.info("⚠️ No tables found in the database.")
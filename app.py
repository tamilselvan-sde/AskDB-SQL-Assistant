import os
import re
import sqlite3
import time
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

# Initialize Groq client with API key from environment variables
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DB_PATH = "Ecommerce.db"

# Function to get the database schema
def fetch_database_schema():
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
        schema_info[table_name] = [col[1] for col in columns]  # Extract column names
    
    conn.close()
    return schema_info

# Function to execute SQL queries
def execute_query(sql_query):
    """Executes the generated SQL query on the database and measures execution time."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        start_time = time.time()  # Start timer
        cursor.execute(sql_query)
        result = cursor.fetchall()
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        column_names = [desc[0] for desc in cursor.description] if cursor.description else []
        conn.close()

        formatted_result = [dict(zip(column_names, row)) for row in result]

        return {
            "execution_time_ms": round(execution_time, 2),
            "result": formatted_result
        }

    except sqlite3.Error as e:
        return {"error": f"SQL Execution Error: {str(e)}"}

# Function to clean AI-generated SQL query
def clean_sql_query(generated_sql):
    """Removes code blocks and unnecessary formatting from AI-generated SQL queries."""
    cleaned_sql = re.sub(r"```sql|```", "", generated_sql, flags=re.IGNORECASE).strip()
    return cleaned_sql

@app.route('/ask', methods=['POST'])
def ask_chat():
    """API endpoint to generate SQL from user query based on schema and execute it."""
    data = request.json
    user_prompt = data.get("question", "").strip()

    if not user_prompt:
        return jsonify({"error": "No question provided"}), 400

    # Get the database schema dynamically
    schema_info = fetch_database_schema()

    # Prepare the optimized prompt with only schema information
    schema_text = "\n".join([f"Table: {table}, Columns: {', '.join(columns)}" for table, columns in schema_info.items()])

    prompt = f"""
You are an SQL expert. Based on the following database schema, generate an optimized SQL query:

{schema_text}

- Generate only the SQL query.
- Do NOT include any explanations or additional text.
- Ensure the query is valid for SQLite.

User's question: "{user_prompt}"
"""

    try:
        # Query the AI model to generate the SQL query
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=500,
            top_p=1
        )

        # Extract and clean the SQL query
        generated_sql = response.choices[0].message.content.strip()
        cleaned_sql = clean_sql_query(generated_sql)

        if not cleaned_sql.upper().startswith("SELECT"):
            return jsonify({"error": "Invalid SQL query generated", "sql": cleaned_sql}), 500

        # Execute the query
        query_result = execute_query(cleaned_sql)

        return jsonify({
            "question": user_prompt,
            "sql_query": cleaned_sql,
            "execution_time_ms": query_result.get("execution_time_ms", 0),
            "actual_result": query_result.get("result", [])
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

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

# Function to analyze query results and suggest a chart type
def analyze_and_suggest_chart(data):
    """
    Analyze the query result to determine the best chart type.
    Returns chart type and relevant data for plotting.
    """
    if not data:
        return None, None, None
    
    # Extract numeric and categorical columns
    numeric_cols = [col for col, dtype in data[0].items() if isinstance(dtype, (int, float))]
    categorical_cols = [col for col, dtype in data[0].items() if isinstance(dtype, str)]
    
    # Determine chart type based on available columns
    if len(numeric_cols) >= 2 and len(categorical_cols) >= 1:
        # Scatter or Line chart
        x_col = categorical_cols[0] if categorical_cols else numeric_cols[0]
        y_col = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]
        chart_type = "scatter" if len(numeric_cols) == 2 else "line"
    elif len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
        # Bar or Pie chart
        x_col = categorical_cols[0]
        y_col = numeric_cols[0]
        chart_type = "bar" if len(categorical_cols) > 1 else "pie"
    else:
        # Default to no chart if insufficient data
        return None, None, None
    
    # Prepare chart data
    chart_data = {
        "x": [row[x_col] for row in data],
        "y": [row[y_col] for row in data]
    }
    return chart_type, chart_data, {"x_col": x_col, "y_col": y_col}

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
You are an SQL expert. Based on the following database schema, generate an optimized SQL query and provide a one-line explanation.
{schema_text}
- First, provide a one-line explanation of what the query does.
- Then, generate only the SQL query.
- Do NOT include any additional text.
- Ensure the query is valid for SQLite.
User's question: "{user_prompt}"
"""
    try:
        # Query the AI model to generate the SQL query and explanation
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=500,
            top_p=1
        )
        # Split explanation and SQL query
        response_text = response.choices[0].message.content.strip().split("\n", 1)
        explanation = response_text[0].strip() if len(response_text) > 1 else "No explanation provided."
        generated_sql = response_text[1].strip() if len(response_text) > 1 else response_text[0]
        cleaned_sql = clean_sql_query(generated_sql)
        
        if not cleaned_sql.upper().startswith("SELECT"):
            return jsonify({"error": "Invalid SQL query generated", "sql": cleaned_sql}), 500
        
        # Execute the query
        query_result = execute_query(cleaned_sql)
        
        # Analyze query results for chart generation
        chart_type, chart_data, chart_columns = analyze_and_suggest_chart(query_result.get("result", []))
        
        return jsonify({
            "question": user_prompt,
            "explanation": explanation,
            "sql_query": cleaned_sql,
            "execution_time_ms": query_result.get("execution_time_ms", 0),
            "actual_result": query_result.get("result", []),
            "chart": {
                "type": chart_type,
                "data": chart_data,
                "columns": chart_columns
            } if chart_type else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
import os
import re
import sqlite3  # Or use MySQL/PostgreSQL based on your DB
from flask import Flask, request, jsonify
from groq import Groq
from query_generator import fetch_all_data

app = Flask(__name__)

# Load all table data into a variable at startup
ALL_DATABASE_DATA = fetch_all_data()

# Initialize Groq client with API key from environment variables
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Database connection function
def execute_query(sql_query):
    """Executes the generated SQL query on the actual database."""
    try:
        conn = sqlite3.connect("Ecommerce.db")  # Change for MySQL/PostgreSQL
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]  # Get column names
        conn.close()

        # Format the result as a list of dictionaries (JSON response)
        formatted_result = [dict(zip(column_names, row)) for row in result]
        return formatted_result

    except sqlite3.Error as e:
        return {"error": f"SQL Execution Error: {str(e)}"}

# Function to clean AI-generated SQL query
def clean_sql_query(generated_sql):
    """Removes code blocks and unnecessary formatting from AI-generated SQL queries."""
    cleaned_sql = re.sub(r"```sql|```", "", generated_sql, flags=re.IGNORECASE).strip()
    return cleaned_sql

@app.route('/ask', methods=['POST'])
def ask_chat():
    """API endpoint to process user queries on stored database data."""
    data = request.json
    user_prompt = data.get("question", "").strip()

    if not user_prompt:
        return jsonify({"error": "No question provided"}), 400

    # Prepare the prompt for Groq
    prompt = "Here is the database schema and data:\n\n"
    for table, table_data in ALL_DATABASE_DATA.items():
        prompt += f"Table: {table}\n"
        prompt += f"Columns: {', '.join(table_data['columns'])}\n"
        prompt += "Data:\n"
        for row in table_data["data"]:
            prompt += f"{', '.join(map(str, row))}\n"
        prompt += "\n"

    prompt += f"""
Now, analyze the given database schema and data carefully.
- **Provide ONLY the SQL query** to answer the question.
- **Do NOT include any explanation, formatting, or extra text.**
- **Only return the SQL query without additional words.**

Question: {user_prompt}
"""

    # Query Groq API for SQL query generation
    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=500,
            top_p=1
        )

        # Extract only the SQL query from Groq response
        generated_sql = response.choices[0].message.content.strip()

        # Clean AI-generated SQL query
        cleaned_sql = clean_sql_query(generated_sql)

        # Validate SQL before execution
        if not cleaned_sql.upper().startswith("SELECT"):
            return jsonify({"error": "Invalid SQL query generated", "sql": cleaned_sql}), 500

        # Execute the cleaned SQL query on the actual database
        query_result = execute_query(cleaned_sql)

        return jsonify({
            "question": user_prompt,
            "sql_query": cleaned_sql,
            "actual_result": query_result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

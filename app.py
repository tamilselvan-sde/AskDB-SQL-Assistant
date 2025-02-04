import os
from flask import Flask, request, jsonify
from groq import Groq
from query_generator import fetch_all_data

app = Flask(__name__)

# Load all table data into a variable at startup
ALL_DATABASE_DATA = fetch_all_data()

# Initialize Groq client with API key from environment variables
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route('/ask', methods=['POST'])
def ask_chat():
    """API endpoint to process user queries on stored database data."""
    data = request.json
    user_prompt = data.get("question", "").strip()

    if not user_prompt:
        return jsonify({"error": "No question provided"}), 400

    # Prepare the prompt to send to Groq API with all table data
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
- Provide the **exact SQL query** required to answer the question. 
- Show the **expected output in tabular format** based on the provided data. 
- Ensure no details are missing in the response. 
- Be precise and return only the most relevant information.

Question: {user_prompt}
"""

    # Query Groq API for an answer
    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",  # Use an appropriate model from Groq
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_tokens=2000,
            top_p=1
        )

        # Extract the answer from the response
        answer = response.choices[0].message.content

        return jsonify({"question": user_prompt, "answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

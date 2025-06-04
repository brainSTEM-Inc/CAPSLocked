from flask import Flask, request, jsonify
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Connect to Neon PostgreSQL
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()

    name = data.get("name")
    topics = data.get("topics")           # list of selected topics
    availability = data.get("availability")  # dict of availability

    try:
        cursor.execute("""
            UPDATE responses
            SET topics = %s, availability = %s
            WHERE name = %s
        """, (str(topics), str(availability), name))

        if cursor.rowcount == 0:
            return jsonify({"message": "Name not found in database"}), 404

        conn.commit()
        return jsonify({"message": "Response saved successfully"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

import os
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# Read database configuration from environment variables
db_name = os.environ.get("POSTGRES_DB", "finance_db")
db_user = os.environ.get("POSTGRES_USER", "user")
db_pass = os.environ.get("POSTGRES_PASSWORD", "pass")
db_host = "db"  # 'db' corresponds to the service name in docker-compose

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_pass,
    host=db_host,
    port="5432"
)
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id SERIAL PRIMARY KEY,
        account_id VARCHAR(50),
        amount NUMERIC,
        flagged BOOLEAN DEFAULT FALSE
    );
""")
conn.commit()

@app.route("/")
def home():
    return "Welcome to the Tech Residency Digital Twin!"

@app.route("/transaction", methods=["POST"])
def transaction():
    data = request.get_json()
    account_id = data.get("account_id", "unknown")
    amount = data.get("amount", 0)
    # Flag transactions over 15,000
    flagged = amount > 15000
    cursor.execute(
        "INSERT INTO transactions (account_id, amount, flagged) VALUES (%s, %s, %s) RETURNING id",
        (account_id, amount, flagged)
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    return jsonify({
        "transaction_id": new_id,
        "account_id": account_id,
        "amount": amount,
        "flagged": flagged
    })

@app.route("/transactions", methods=["GET"])
def list_transactions():
    cursor.execute("SELECT id, account_id, amount, flagged FROM transactions ORDER BY id DESC")
    rows = cursor.fetchall()
    results = [{
        "id": row[0],
        "account_id": row[1],
        "amount": float(row[2]),
        "flagged": row[3]
    } for row in rows]
    return jsonify(results)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
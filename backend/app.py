from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__, static_folder='../frontend')
CORS(app)  # Allow frontend to access API

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",        # 'mysql-db' if using Docker Compose
            user="root",
            password="admin",
            database="mydatabase"
        )
        return conn
    except Error as e:
        print(f"DB connection error: {e}")
        return None

# -------------------- Serve Frontend --------------------
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# -------------------- CRUD APIs --------------------
@app.route("/users", methods=["GET"])
def view_users():
    print("Fetching users from database")
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    print("DB connection established")
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    print("Query executed")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

@app.route("/users", methods=["POST"])
def add_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name,email) VALUES (%s,%s)", (name,email))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "User added successfully"}), 201

@app.route("/users/<int:user_id>", methods=["PUT"])
def edit_user(user_id):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name=%s, email=%s WHERE id=%s", (name, email, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "User updated successfully"})

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "User deleted successfully"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

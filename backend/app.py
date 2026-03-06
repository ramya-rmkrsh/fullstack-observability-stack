import os
import logging
import psycopg2
import json
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request
from ddtrace import patch_all, tracer
from flask_cors import CORS

# 🔍 Enable Datadog auto-instrumentation
patch_all()

app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": "http://localhost:8080"}}
)

# 📜 Basic structured logging (stdout → Datadog picks this up)

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,       # ← DD reads this to set status
            "logger": record.name,
            "message": record.getMessage(),
            "service": "backend"
        })

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])

logger = logging.getLogger("user-crud-app")

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        port=os.environ.get("DB_PORT"),
        cursor_factory=RealDictCursor
    )

def init_db():
    logger.info("Initializing database")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    logger.info("Database initialized")

@app.before_request
def log_request():
    logger.info(
        "Incoming request",
        extra={
            "method": request.method,
            "path": request.path,
            "remote_addr": request.remote_addr
        }
    )

@app.route("/users", methods=["GET"])
def get_users():
    logger.info("Fetching users")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users ORDER BY id")
    users = cur.fetchall()
    cur.close()
    conn.close()
    logger.info("Fetched %s users", len(users))
    if not users:
        logger.warning("No users found in database")
        return jsonify([]), 200
    return jsonify(users),200


@app.route("/users", methods=["POST"])
def add_user():
    log = logging.LoggerAdapter(logger, {"user_name": "-"})
    log.info("POST /users HIT")
    try:
        data = request.get_json()
        log = logging.LoggerAdapter(logger, {"user_name": data.get("name")})
        log.info("Adding users request")
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (data["name"], data["email"])
        )
        conn.commit()
        cur.close()
        conn.close()
        logger.info("User added successfully")
        return jsonify({"message": "User added successfully"}), 201
    
    except Exception as e:
        logger.error("Error adding user: %s", str(e))
        return jsonify({"error": "Failed to add user"}), 200
 

@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        data = request.get_json()
        logger.info("Updating user", extra={"user_id": user_id})

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET name=%s, email=%s WHERE id=%s",
            (data["name"], data["email"], user_id)
        )
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "User updated successfully"}),204
    
    except Exception as e:
        logger.error("Error updating user: %s", str(e))
        return jsonify({"error": "Failed to update user"}), 200
    

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        logger.info("Deleting user", extra={"user_id": user_id})

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "User deleted successfully"}), 204
    
    except Exception as e:
        logger.error("Error deleting user: %s", str(e))
        return jsonify({"error": "Failed to delete user"}), 200

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)

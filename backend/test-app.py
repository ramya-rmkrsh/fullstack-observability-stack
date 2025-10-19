import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="appuser",
    password="app123",
    database="mydatabase"
)

print("DB connection established")
cursor = conn.cursor()
cursor.execute("SHOW TABLES;")
print(cursor.fetchall())
print("Query executed")
cursor.close()
conn.close()


import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    port=3307,
    user="root",
    password="Root@1234",
    database="queue_management_db"
)

print("Connected Successfully!")
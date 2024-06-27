import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="roxana",
    password="pass",
    database="licenta"
)

cursor = db.cursor()
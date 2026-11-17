
import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=input("Enter MySQL password: "),
    database="hospitality_analytics"
)

if connection.is_connected():
    print("Successfully connected to Hospitality Analytics!")

    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")

    print("\nAvailable tables:")
    for table in cursor.fetchall():
        print(table[0])

    cursor.close()
    connection.close()

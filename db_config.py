import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="SiddhiRoot06@",
        database="organ_donation_db"
    )

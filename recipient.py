from db_config import get_db_connection

def add_recipient():
    db = get_db_connection()
    cursor = db.cursor()
    print("\n--- Add Recipient ---")
    name = input("Enter recipient name: ")
    age = int(input("Enter recipient age: "))
    gender = input("Enter recipient gender (Male/Female/Other): ")
    blood_group = input("Enter recipient blood group (e.g., A+, B-): ")
    organ_needed = input("Enter required organ: ")  # Updated column name
    contact_info = input("Enter contact info (Phone/Email): ")
    city = input("Enter city: ")

    query = """
        INSERT INTO recipient (name, age, gender, blood_group, organ_needed, contact_info, city)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (name, age, gender, blood_group, organ_needed, contact_info, city)

    cursor.execute(query, values)
    db.commit()
    print("✅ Recipient added successfully!")

    cursor.close()
    db.close()

def view_recipients():
    db = get_db_connection()
    cursor = db.cursor()
    print("\n--- List of Recipients ---")
    cursor.execute("SELECT * FROM recipient")
    recipients = cursor.fetchall()

    for recipient in recipients:
        print(recipient)

    cursor.close()
    db.close()

def update_recipient():
    db = get_db_connection()
    cursor = db.cursor()
    print("\n--- Update Recipient ---")
    recipient_id = input("Enter recipient ID to update: ")
    new_city = input("Enter new city: ")

    query = "UPDATE recipient SET city = %s WHERE recipient_id = %s"
    values = (new_city, recipient_id)

    cursor.execute(query, values)
    db.commit()
    print("✅ Recipient updated successfully!")

    cursor.close()
    db.close()

def delete_recipient():
    db = get_db_connection()
    cursor = db.cursor()
    print("\n--- Delete Recipient ---")
    recipient_id = input("Enter recipient ID to delete: ")

    query = "DELETE FROM recipient WHERE recipient_id = %s"
    cursor.execute(query, (recipient_id,))
    db.commit()
    print("✅ Recipient deleted successfully!")

    cursor.close()
    db.close()

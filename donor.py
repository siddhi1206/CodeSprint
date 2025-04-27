from db_config import get_db_connection

def add_donor():
    db = get_db_connection()
    cursor = db.cursor()
    print("\n--- Add Donor ---")
    name = input("Enter donor name: ")
    age = int(input("Enter donor age: "))
    gender = input("Enter donor gender (Male/Female/Other): ")
    blood_group = input("Enter donor blood group (e.g., A+, B-): ")
    organ_donated = input("Enter organ to donate: ")
    contact_info = input("Enter contact info (Phone/Email): ")
    city = input("Enter city: ")

    query = """
        INSERT INTO donor (name, age, gender, blood_group, organ_donated, contact_info, city)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (name, age, gender, blood_group, organ_donated, contact_info, city)

    cursor.execute(query, values)
    db.commit()
    print("✅ Donor added successfully!")

    cursor.close()
    db.close()


def view_donors():
    db = get_db_connection()
    cursor = db.cursor()
    print("\n--- List of Donors ---")
    cursor.execute("SELECT * FROM donor")
    donors = cursor.fetchall()

    for donor in donors:
        print(donor)

    cursor.close()
    db.close()

def update_donor():
    db = get_db_connection()
    cursor = db.cursor()
    print("\n--- Update Donor ---")
    donor_id = input("Enter donor ID to update: ")
    new_city = input("Enter new city: ")

    query = "UPDATE donor SET city = %s WHERE donor_id = %s"
    values = (new_city, donor_id)

    cursor.execute(query, values)
    db.commit()
    print("✅ Donor updated successfully!")

    cursor.close()
    db.close()

def delete_donor():
    db = get_db_connection()
    cursor = db.cursor()
    print("\n--- Delete Donor ---")
    donor_id = input("Enter donor ID to delete: ")

    query = "DELETE FROM donor WHERE donor_id = %s"
    cursor.execute(query, (donor_id,))
    db.commit()
    print("✅ Donor deleted successfully!")

    cursor.close()
    db.close()

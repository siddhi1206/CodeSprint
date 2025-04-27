from db_config import get_db_connection

def match_organ():
    db = get_db_connection()
    cursor = db.cursor()
    print("\n--- Matching Donors and Recipients ---")
    organ_needed = input("Enter required organ: ")
    blood_group = input("Enter recipient's blood group (e.g., A+, B-): ")

    query = """
        SELECT * FROM donor 
        WHERE organ_donated = %s AND blood_group = %s AND donation_status = 'Available'
    """
    values = (organ_needed, blood_group)

    cursor.execute(query, values)
    matches = cursor.fetchall()

    if matches:
        print("\n✅ Matching Donors Found:")
        for match in matches:
            print(match)
    else:
        print("\n❌ No matching donor found.")

    cursor.close()
    db.close()

def record_donation():
    db = get_db_connection()
    cursor = db.cursor()
    print("\n--- Record Donation ---")
    donor_id = input("Enter Donor ID: ")
    recipient_id = input("Enter Recipient ID: ")
    organ = input("Enter Organ donated: ")
    date = input("Enter Date of Donation (YYYY-MM-DD): ")

    # Insert into organ_donation table
    query = """
        INSERT INTO organ_donation (donor_id, recipient_id, organ, date_of_donation)
        VALUES (%s, %s, %s, %s)
    """
    values = (donor_id, recipient_id, organ, date)
    cursor.execute(query, values)

    # Also update donor table: mark donor as Not Available
    update_query = """
        UPDATE donor
        SET donation_status = 'Donated'
        WHERE donor_id = %s
    """
    cursor.execute(update_query, (donor_id,))

    db.commit()
    print("✅ Donation recorded successfully and donor status updated!")

    cursor.close()
    db.close()

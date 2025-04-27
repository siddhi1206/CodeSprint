from donor import add_donor, view_donors
from recipient import add_recipient, view_recipients
from donation import match_organ, record_donation

def main_menu():
    while True:
        print("\n--- Organ Donation Management System ---")
        print("1. Add Donor")
        print("2. View Donors")
        print("3. Add Recipient")
        print("4. View Recipients")
        print("5. Match Organ")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            add_donor()
        elif choice == '2':
            view_donors()
        elif choice == '3':
            add_recipient()
        elif choice == '4':
            view_recipients()
        elif choice == '5':
            match_organ()
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main_menu()

from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os
from functools import wraps
import json
from datetime import datetime
from datetime import datetime, timedelta
app = Flask(__name__)
app.secret_key = os.urandom(24)


# Database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',  # Change this to your MySQL password
        database='organ_donation_db'
    )
    return connection


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in first', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# Routes
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            session['username'] = username
            flash('You have been logged in successfully', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('home'))


def get_time_ago(timestamp):
    """Convert timestamp to '2 hours ago' format"""
    now = datetime.now()
    diff = now - timestamp

    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=1):
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff < timedelta(days=1):
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff < timedelta(days=30):
        days = diff.days
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        return timestamp.strftime("%Y-%m-%d")

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get total donors
    cursor.execute("SELECT COUNT(*) as count FROM donor")
    total_donors = cursor.fetchone()['count']

    # Get total recipients
    cursor.execute("SELECT COUNT(*) as count FROM recipient")
    total_recipients = cursor.fetchone()['count']

    # Get successful matches
    cursor.execute("SELECT COUNT(*) as count FROM organ_donation")
    successful_matches = cursor.fetchone()['count']

    # Get organ availability
    # For this example, we'll count available organs by type from the donor table
    cursor.execute("""
        SELECT organ_donated as name, COUNT(*) as count 
        FROM donor 
        WHERE donation_status = 'Available'
        GROUP BY organ_donated
    """)
    organ_data = cursor.fetchall()

    # Calculate max for percentage bars
    max_count = 1  # Default to 1 to avoid division by zero
    if organ_data:
        max_count = max(item['count'] for item in organ_data)

    organ_availability = []
    for organ in organ_data:
        organ_availability.append({
            'name': organ['name'],
            'count': organ['count'],
            'percentage': int((organ['count'] / max_count) * 100)
        })

    # Get recent activities
    activities = []

    # Recent donations/matches
    cursor.execute("""
        SELECT od.created_at, d.name as donor_name, r.name as recipient_name, od.organ
        FROM organ_donation od
        JOIN donor d ON od.donor_id = d.donor_id
        JOIN recipient r ON od.recipient_id = r.recipient_id
        ORDER BY od.created_at DESC LIMIT 3
    """)

    for match in cursor.fetchall():
        activities.append({
            'icon': 'fa-check-circle',
            'title': f"{match['recipient_name']} matched with donor {match['donor_name']}",
            'description': f"{match['organ']} transplant match successfully recorded",
            'time_ago': get_time_ago(match['created_at'])
        })

    # Recent recipients added
    cursor.execute("""
        SELECT name, created_at FROM recipient ORDER BY created_at DESC LIMIT 3
    """)

    for recipient in cursor.fetchall():
        activities.append({
            'icon': 'fa-user-plus',
            'title': "New recipient added",
            'description': f'Recipient "{recipient["name"]}" added to the system',
            'time_ago': get_time_ago(recipient['created_at'])
        })

    # Recent donors added
    cursor.execute("""
        SELECT name, created_at FROM donor ORDER BY created_at DESC LIMIT 3
    """)

    for donor in cursor.fetchall():
        activities.append({
            'icon': 'fa-user-plus',
            'title': "New donor added",
            'description': f'Donor "{donor["name"]}" added to the system',
            'time_ago': get_time_ago(donor['created_at'])
        })

    # Sort activities by timestamp (newest first) and take top 5
    activities.sort(key=lambda x: x['time_ago'])
    activities = activities[:5]

    cursor.close()
    conn.close()

    return render_template('dashboard.html',
                           admin_name=session['username'],
                           total_donors=total_donors,
                           total_recipients=total_recipients,
                           successful_matches=successful_matches,
                           organ_availability=organ_availability,
                           activities=activities)


# Update the donors route to include statistics
@app.route('/donors')
@login_required
def donors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get all donors
    cursor.execute('SELECT * FROM donor')
    donors = cursor.fetchall()

    # Calculate donor statistics
    stats = {}

    # Total donors
    cursor.execute('SELECT COUNT(*) as total FROM donor')
    stats['total_donors'] = cursor.fetchone()['total']

    # Available donors
    cursor.execute("SELECT COUNT(*) as available FROM donor WHERE donation_status = 'Available'")
    stats['available_donors'] = cursor.fetchone()['available']

    # Completed donations
    cursor.execute("SELECT COUNT(*) as donated FROM donor WHERE donation_status = 'Donated'")
    stats['completed_donations'] = cursor.fetchone()['donated']

    # This month's donors
    cursor.execute(
        "SELECT COUNT(*) as this_month FROM donor WHERE MONTH(registration_date) = MONTH(CURRENT_DATE()) AND YEAR(registration_date) = YEAR(CURRENT_DATE())")
    stats['this_month'] = cursor.fetchone()['this_month']

    cursor.close()
    conn.close()

    return render_template('donors.html', donors=donors, stats=stats)

@app.route('/add_donor', methods=['GET', 'POST'])
@login_required
def add_donor():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        blood_group = request.form['blood_group']
        organ_donated = request.form['organ_donated']
        contact_info = request.form['contact_info']
        city = request.form['city']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO donor (name, age, gender, blood_group, organ_donated, contact_info, city, donation_status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (name, age, gender, blood_group, organ_donated, contact_info, city, 'Available'))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Donor added successfully', 'success')
        return redirect(url_for('donors'))

    return render_template('add_donor.html')


@app.route('/edit_donor/<int:donor_id>', methods=['GET', 'POST'])
@login_required
def edit_donor(donor_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        blood_group = request.form['blood_group']
        organ_donated = request.form['organ_donated']
        contact_info = request.form['contact_info']
        city = request.form['city']
        donation_status = request.form['donation_status']

        cursor.execute('''
            UPDATE donor 
            SET name=%s, age=%s, gender=%s, blood_group=%s, organ_donated=%s, contact_info=%s, city=%s, donation_status=%s 
            WHERE donor_id=%s
        ''', (name, age, gender, blood_group, organ_donated, contact_info, city, donation_status, donor_id))
        conn.commit()
        flash('Donor updated successfully', 'success')
        return redirect(url_for('donors'))

    cursor.execute('SELECT * FROM donor WHERE donor_id = %s', (donor_id,))
    donor = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('edit_donor.html', donor=donor)


@app.route('/view_donor/<int:donor_id>')
@login_required
def view_donor(donor_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM donor WHERE donor_id = %s', (donor_id,))
    donor = cursor.fetchone()
    cursor.close()
    conn.close()

    if donor:
        return render_template('view_donor.html', donor=donor)
    else:
        flash('Donor not found', 'danger')
        return redirect(url_for('donors'))


@app.route('/delete_donor/<int:donor_id>')
@login_required
def delete_donor(donor_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM donor WHERE donor_id = %s', (donor_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Donor deleted successfully', 'success')
    return redirect(url_for('donors'))


from datetime import datetime


# Recipient Management Routes
@app.route('/recipients')
@login_required
def recipients():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get all recipients
    cursor.execute('SELECT * FROM recipient')
    recipients = cursor.fetchall()

    # Calculate statistics
    stats = {
        'total_recipients': 0,
        'waiting_recipients': 0,
        'matched_recipients': 0,
        'urgent_cases': 0
    }

    # Count statistics from recipients data
    stats['total_recipients'] = len(recipients)
    for recipient in recipients:
        if recipient['status'] == 'Waiting':
            stats['waiting_recipients'] += 1
        elif recipient['status'] == 'Matched':
            stats['matched_recipients'] += 1
        elif recipient['status'] == 'Urgent':
            stats['urgent_cases'] += 1

    cursor.close()
    conn.close()

    return render_template('recipients.html', recipients=recipients, stats=stats)


@app.route('/add_recipient', methods=['GET', 'POST'])
@login_required
def add_recipient():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        blood_group = request.form['blood_group']
        organ_needed = request.form['organ_needed']
        contact_info = request.form['contact_info']
        city = request.form['city']
        urgency_level = request.form.get('urgency_level', 'Normal')

        # Set status based on urgency level
        status = 'Urgent' if urgency_level in ['Urgent', 'Critical'] else 'Waiting'

        # Add current date as registration date
        registration_date = datetime.now().strftime('%Y-%m-%d')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO recipient (name, age, gender, blood_group, organ_needed, contact_info, city, status, registration_date) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
        name, age, gender, blood_group, organ_needed, contact_info, city, status, registration_date))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Recipient added successfully', 'success')
        return redirect(url_for('recipients'))

    return render_template('add_recipient.html')


@app.route('/edit_recipient/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def edit_recipient(recipient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        blood_group = request.form['blood_group']
        organ_needed = request.form['organ_needed']
        contact_info = request.form['contact_info']
        city = request.form['city']
        status = request.form['status']


        # Get the existing record to check registration_date
        cursor.execute('SELECT registration_date FROM recipient WHERE recipient_id = %s', (recipient_id,))
        existing_record = cursor.fetchone()

        # If registration_date is NULL, update it with current date
        if not existing_record['registration_date']:
            registration_date = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                UPDATE recipient 
                SET name=%s, age=%s, gender=%s, blood_group=%s, organ_needed=%s, contact_info=%s, city=%s, status=%s, registration_date=%s 
                WHERE recipient_id=%s
            ''', (name, age, gender, blood_group, organ_needed, contact_info, city, status, registration_date, recipient_id))
        else:
            cursor.execute('''
                UPDATE recipient 
                SET name=%s, age=%s, gender=%s, blood_group=%s, organ_needed=%s, contact_info=%s, city=%s, status=%s
                WHERE recipient_id=%s
            ''', (
            name, age, gender, blood_group, organ_needed, contact_info, city, status, recipient_id))

        conn.commit()
        flash('Recipient updated successfully', 'success')
        return redirect(url_for('recipients'))

    cursor.execute('SELECT * FROM recipient WHERE recipient_id = %s', (recipient_id,))
    recipient = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('edit_recipient.html', recipient=recipient)


@app.route('/view_recipient/<int:recipient_id>')
@login_required
def view_recipient(recipient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM recipient WHERE recipient_id = %s', (recipient_id,))
    recipient = cursor.fetchone()
    cursor.close()
    conn.close()

    if recipient:
        return render_template('view_recipient.html', recipient=recipient)
    else:
        flash('Recipient not found', 'danger')
        return redirect(url_for('recipients'))


@app.route('/delete_recipient/<int:recipient_id>')
@login_required
def delete_recipient(recipient_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM recipient WHERE recipient_id = %s', (recipient_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Recipient deleted successfully', 'success')
    return redirect(url_for('recipients'))


# Helper function for blood type compatibility
def get_compatible_blood_groups(donor_blood_group):
    """
    Returns a list of recipient blood groups compatible with the donor blood group
    Based on blood type compatibility rules for organ donation
    """
    # Blood type compatibility chart (from donor to recipient)
    compatibility = {
        'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],  # Universal donor
        'O+': ['O+', 'A+', 'B+', 'AB+'],
        'A-': ['A-', 'A+', 'AB-', 'AB+'],
        'A+': ['A+', 'AB+'],
        'B-': ['B-', 'B+', 'AB-', 'AB+'],
        'B+': ['B+', 'AB+'],
        'AB-': ['AB-', 'AB+'],
        'AB+': ['AB+']  # Universal recipient
    }

    return compatibility.get(donor_blood_group, [])


# Helper function for blood type compatibility (from recipient to donor)
def get_compatible_donor_blood_groups(recipient_blood_group):
    """
    Returns a list of donor blood groups compatible with the recipient blood group
    Based on blood type compatibility rules for organ donation
    """
    # Blood type compatibility chart (from recipient to donor)
    compatibility = {
        'O-': ['O-'],  # O- can only receive from O-
        'O+': ['O-', 'O+'],  # O+ can receive from O+, O-
        'A-': ['O-', 'A-'],  # A- can receive from A-, O-
        'A+': ['O-', 'O+', 'A-', 'A+'],  # A+ can receive from A+, A-, O+, O-
        'B-': ['O-', 'B-'],  # B- can receive from B-, O-
        'B+': ['O-', 'O+', 'B-', 'B+'],  # B+ can receive from B+, B-, O+, O-
        'AB-': ['O-', 'A-', 'B-', 'AB-'],  # AB- can receive from AB-, A-, B-, O-
        'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']  # AB+ can receive from all
    }

    return compatibility.get(recipient_blood_group, [])


@app.route('/organ_matching', methods=['GET', 'POST'])
@login_required
def organ_matching():
    recipients = []
    matching_donors = []
    selected_recipient = None
    organs = []
    blood_groups = []
    statuses = []  # New list to store recipient statuses

    # Define the blood compatibility function
    def get_compatible_donor_blood_groups(recipient_blood_group):
        # Blood compatibility chart: recipient can receive from these donor groups
        compatibility = {
            'A+': ['A+', 'A-', 'O+', 'O-'],
            'A-': ['A-', 'O-'],
            'B+': ['B+', 'B-', 'O+', 'O-'],
            'B-': ['B-', 'O-'],
            'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],  # Universal recipient
            'AB-': ['A-', 'B-', 'AB-', 'O-'],
            'O+': ['O+', 'O-'],
            'O-': ['O-']  # Universal donor
        }
        return compatibility.get(recipient_blood_group, [])

    try:
        # Get DB connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get the list of organs for the dropdown
        cursor.execute("SELECT DISTINCT organ_needed FROM recipient")  # Removed WHERE status = 'Waiting'
        organs = [row['organ_needed'] for row in cursor.fetchall()]

        # Get the list of blood groups for the dropdown
        cursor.execute("SELECT DISTINCT blood_group FROM recipient")  # Removed WHERE status = 'Waiting'
        blood_groups = [row['blood_group'] for row in cursor.fetchall()]

        # Get the list of statuses for the dropdown
        cursor.execute("SELECT DISTINCT status FROM recipient")
        statuses = [row['status'] for row in cursor.fetchall()]

        if request.method == 'POST':
            recipient_id = request.form.get('recipient_id')
            organ_type = request.form.get('organ_type')
            blood_group = request.form.get('blood_group')
            status = request.form.get('status')  # New parameter for status filtering

            # Search conditions
            conditions = []
            params = []

            # Filter by organ type if provided
            if organ_type:
                conditions.append("organ_needed = %s")
                params.append(organ_type)

            # Filter by blood group if provided
            if blood_group:
                conditions.append("blood_group = %s")
                params.append(blood_group)

            # Filter by status if provided
            if status:
                conditions.append("status = %s")
                params.append(status)

            # If recipient ID is provided, get that specific recipient
            if recipient_id:
                cursor.execute('''
                    SELECT recipient_id, name, 
                           name AS full_name,
                           age, blood_group, organ_needed, city, status
                    FROM recipient 
                    WHERE recipient_id = %s
                ''', (recipient_id,))
                selected_recipient = cursor.fetchone()

                if selected_recipient:
                    # Find compatible donors for this recipient
                    compatible_blood_groups = get_compatible_donor_blood_groups(selected_recipient['blood_group'])

                    if compatible_blood_groups:
                        placeholders = ', '.join(['%s'] * len(compatible_blood_groups))
                        donor_query = f'''
                            SELECT donor_id, name,
                                   name AS full_name,
                                   age, gender, blood_group, organ_donated, city, donation_status
                            FROM donor 
                            WHERE blood_group IN ({placeholders}) 
                            AND organ_donated = %s 
                            AND donation_status = 'Available'
                        '''

                        # Add organ_needed and compatible blood groups as parameters
                        donor_params = list(compatible_blood_groups)
                        donor_params.append(selected_recipient['organ_needed'])

                        cursor.execute(donor_query, donor_params)
                        matching_donors = cursor.fetchall()

                        if not matching_donors:
                            flash(
                                f'No compatible donors found for recipient {selected_recipient["full_name"]} (Blood Group: {selected_recipient["blood_group"]}, Organ: {selected_recipient["organ_needed"]})',
                                'info')
            else:
                # Build query with conditions
                if conditions:
                    query = f'''
                        SELECT recipient_id, name, 
                               name AS full_name,
                               age, blood_group, organ_needed, city, status
                        FROM recipient 
                        WHERE {' AND '.join(conditions)}
                    '''
                    cursor.execute(query, params)
                    recipients = cursor.fetchall()

                    if not recipients:
                        filter_description = ""
                        if organ_type:
                            filter_description += f" Organ: {organ_type}"
                        if blood_group:
                            filter_description += f" Blood Group: {blood_group}"
                        if status:
                            filter_description += f" Status: {status}"
                        flash(f'No recipients found for the selected criteria.{filter_description}', 'info')
                else:
                    # Get all recipients if no filters are provided
                    cursor.execute('''
                        SELECT recipient_id, name, 
                               name AS full_name,
                               age, blood_group, organ_needed, city, status
                        FROM recipient
                    ''')  # Removed WHERE status = 'Waiting'
                    recipients = cursor.fetchall()

        else:
            # For GET requests, show all recipients
            cursor.execute('''
                SELECT recipient_id, name, 
                       name AS full_name,
                       age, blood_group, organ_needed, city, status
                FROM recipient
            ''')  # Removed WHERE status = 'Waiting'
            recipients = cursor.fetchall()

    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

    return render_template('organ_matching.html',
                           recipients=recipients,
                           matching_donors=matching_donors,
                           selected_recipient=selected_recipient,
                           organs=organs,
                           blood_groups=blood_groups,
                           statuses=statuses)  # Added statuses to template context


@app.route('/record_donation', methods=['POST'])
@login_required
def record_donation():
    donor_id = request.form.get('donor_id')
    recipient_id = request.form.get('recipient_id')

    # Validate that we have both IDs
    if not donor_id or not recipient_id:
        flash('Missing donor or recipient information', 'danger')
        return redirect(url_for('organ_matching'))

    # Define the blood compatibility function within this route too
    def get_compatible_donor_blood_groups(recipient_blood_group):
        # Blood compatibility chart: recipient can receive from these donor groups
        compatibility = {
            'A+': ['A+', 'A-', 'O+', 'O-'],
            'A-': ['A-', 'O-'],
            'B+': ['B+', 'B-', 'O+', 'O-'],
            'B-': ['B-', 'O-'],
            'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],  # Universal recipient
            'AB-': ['A-', 'B-', 'AB-', 'O-'],
            'O+': ['O+', 'O-'],
            'O-': ['O-']  # Universal donor
        }
        return compatibility.get(recipient_blood_group, [])

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verify donor exists and is available
        cursor.execute('SELECT * FROM donor WHERE donor_id = %s AND donation_status = "Available"', (donor_id,))
        donor = cursor.fetchone()

        # Verify recipient exists (removed the AND status = "Waiting" restriction)
        cursor.execute('SELECT * FROM recipient WHERE recipient_id = %s', (recipient_id,))
        recipient = cursor.fetchone()

        if not donor or not recipient:
            flash('Selected donor or recipient is no longer available', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('organ_matching'))

        # Check if the recipient is already matched
        if recipient['status'] == 'Matched':
            flash('This recipient has already been matched with a donor. Please select another recipient.', 'warning')
            cursor.close()
            conn.close()
            return redirect(url_for('organ_matching'))

        # Verify blood compatibility
        compatible_blood_groups = get_compatible_donor_blood_groups(recipient['blood_group'])
        if donor['blood_group'] not in compatible_blood_groups:
            flash('Blood type incompatibility detected. Donation cannot proceed.', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('organ_matching'))

        # Verify organ compatibility
        if donor['organ_donated'] != recipient['organ_needed']:
            flash('Organ type mismatch. Donation cannot proceed.', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('organ_matching'))

        # Update donor status
        cursor.execute('''
            UPDATE donor 
            SET donation_status = 'Donated' 
            WHERE donor_id = %s
        ''', (donor_id,))

        # Update recipient status
        cursor.execute('''
            UPDATE recipient 
            SET status = 'Matched' 
            WHERE recipient_id = %s
        ''', (recipient_id,))

        # Get the table structure to check the available columns
        cursor.execute("DESCRIBE organ_donation")
        columns = [column['Field'] for column in cursor.fetchall()]

        # Construct the SQL query based on available columns
        if 'date_of_donation' in columns:
            cursor.execute('''
                INSERT INTO organ_donation (donor_id, recipient_id, organ, date_of_donation) 
                VALUES (%s, %s, %s, CURDATE())
            ''', (donor_id, recipient_id, recipient['organ_needed']))
        else:
            # Alternative query without the date_of_donation column
            cursor.execute('''
                INSERT INTO organ_donation (donor_id, recipient_id, organ) 
                VALUES (%s, %s, %s)
            ''', (donor_id, recipient_id, recipient['organ_needed']))

        conn.commit()
        flash(f'Organ donation recorded successfully. Donor {donor["name"]} to Recipient {recipient["name"]}',
              'success')
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback()
        flash(f'Error recording donation: {str(e)}', 'danger')
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

    return redirect(url_for('organ_matching'))

@app.route('/reports')
@login_required
def reports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get basic statistics
    stats = {}

    # Total donors
    cursor.execute('SELECT COUNT(*) as total FROM donor')
    stats['total_donors'] = cursor.fetchone()['total']

    # Available donors
    cursor.execute("SELECT COUNT(*) as available FROM donor WHERE donation_status = 'Available'")
    stats['available_donors'] = cursor.fetchone()['available']

    # Total recipients
    cursor.execute('SELECT COUNT(*) as total FROM recipient')
    stats['total_recipients'] = cursor.fetchone()['total']

    # Completed donations
    cursor.execute("SELECT COUNT(*) as donated FROM donor WHERE donation_status = 'Donated'")
    stats['completed_donations'] = cursor.fetchone()['donated']

    # Chart data

    # Organ type distribution
    cursor.execute('''
        SELECT organ_donated, COUNT(*) as count 
        FROM donor 
        GROUP BY organ_donated
    ''')

    organ_types = cursor.fetchall()
    organ_stats = []
    for organ in organ_types:
        if organ['organ_donated'] and organ['count']:
            organ_stats.append(organ['count'])

    # Monthly donation statistics for the current year
    current_year = datetime.now().year
    monthly_stats = [0] * 12

    cursor.execute('''
        SELECT MONTH(registration_date) as month, COUNT(*) as count
        FROM donor
        WHERE YEAR(registration_date) = %s
        GROUP BY MONTH(registration_date)
    ''', (current_year,))

    monthly_data = cursor.fetchall()
    for item in monthly_data:
        if item['month'] and item['count']:
            monthly_stats[item['month'] - 1] = item['count']

    # Blood type distribution for donors
    blood_types = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
    blood_donor_stats = [0] * len(blood_types)
    blood_recipient_stats = [0] * len(blood_types)

    for i, blood_type in enumerate(blood_types):
        # Donors with this blood type
        cursor.execute('''
            SELECT COUNT(*) as count FROM donor
            WHERE blood_group = %s
        ''', (blood_type,))
        result = cursor.fetchone()
        if result and 'count' in result:
            blood_donor_stats[i] = result['count']

        # Recipients with this blood type
        cursor.execute('''
            SELECT COUNT(*) as count FROM recipient
            WHERE blood_group = %s
        ''', (blood_type,))
        result = cursor.fetchone()
        if result and 'count' in result:
            blood_recipient_stats[i] = result['count']

    cursor.close()
    conn.close()

    # Convert data to JSON strings for the template
    organ_stats_json = json.dumps(organ_stats)
    monthly_stats_json = json.dumps(monthly_stats)
    blood_donor_stats_json = json.dumps(blood_donor_stats)
    blood_recipient_stats_json = json.dumps(blood_recipient_stats)

    return render_template('reports.html',
                           stats=stats,
                           organ_stats=organ_stats_json,
                           monthly_stats=monthly_stats_json,
                           blood_donor_stats=blood_donor_stats_json,
                           blood_recipient_stats=blood_recipient_stats_json)

if __name__ == '__main__':
    app.run(debug=True)

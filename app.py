from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os
from functools import wraps
import json
from datetime import datetime
app = Flask(__name__)
app.secret_key = os.urandom(24)


# Database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='SiddhiRoot06@',  # Change this to your MySQL password
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


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


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




# Recipient Management Routes
@app.route('/recipients')
@login_required
def recipients():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM recipient')
    recipients = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('recipients.html', recipients=recipients)


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

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO recipient (name, age, gender, blood_group, organ_needed, contact_info, city, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (name, age, gender, blood_group, organ_needed, contact_info, city, 'Waiting'))
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

        cursor.execute('''
            UPDATE recipient 
            SET name=%s, age=%s, gender=%s, blood_group=%s, organ_needed=%s, contact_info=%s, city=%s, status=%s 
            WHERE recipient_id=%s
        ''', (name, age, gender, blood_group, organ_needed, contact_info, city, status, recipient_id))
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


# Organ Matching Route
# Organ Matching Route
@app.route('/organ_matching', methods=['GET', 'POST'])
@login_required
def organ_matching():
    matches = []
    available_donors = []
    selected_donor = None

    # Get all available donors for the dropdown
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM donor WHERE donation_status = 'Available'")
    available_donors = cursor.fetchall()

    if request.method == 'POST':
        blood_group = request.form['blood_group']
        organ_type = request.form['organ_type']
        donor_id = request.form.get('donor_id')

        # If donor_id is selected, get donor details
        if donor_id:
            cursor.execute('SELECT * FROM donor WHERE donor_id = %s', (donor_id,))
            selected_donor = cursor.fetchone()

            # Use the donor's blood group and organ type if selected
            if selected_donor:
                blood_group = selected_donor['blood_group']
                organ_type = selected_donor['organ_donated']

        # Find matching recipients based on blood group and organ needed
        # For blood group compatibility
        compatible_blood_groups = get_compatible_blood_groups(blood_group)

        placeholders = ', '.join(['%s'] * len(compatible_blood_groups))
        query = f'''
            SELECT * FROM recipient 
            WHERE blood_group IN ({placeholders}) AND organ_needed = %s AND status = 'Waiting'
        '''

        # Add organ_type as the last parameter
        cursor.execute(query, (*compatible_blood_groups, organ_type))
        matches = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('organ_matching.html',
                           matches=matches,
                           available_donors=available_donors,
                           selected_donor=selected_donor)


# Helper function for blood type compatibility
def get_compatible_blood_groups(donor_blood_group):
    # Blood type compatibility chart
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


@app.route('/record_donation', methods=['POST'])
@login_required
def record_donation():
    donor_id = request.form['donor_id']
    recipient_id = request.form['recipient_id']

    # Validate that we have both IDs
    if not donor_id or not recipient_id:
        flash('Missing donor or recipient information', 'danger')
        return redirect(url_for('organ_matching'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Verify donor exists and is available
    cursor.execute('SELECT * FROM donor WHERE donor_id = %s AND donation_status = "Available"', (donor_id,))
    donor = cursor.fetchone()

    # Verify recipient exists and is waiting
    cursor.execute('SELECT * FROM recipient WHERE recipient_id = %s AND status = "Waiting"', (recipient_id,))
    recipient = cursor.fetchone()

    if not donor or not recipient:
        flash('Selected donor or recipient is no longer available', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('organ_matching'))

    try:
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

        # Record donation in organ_donation table
        cursor.execute('''
            INSERT INTO organ_donation (donor_id, recipient_id, donation_date) 
            VALUES (%s, %s, CURRENT_DATE())
        ''', (donor_id, recipient_id))

        conn.commit()
        flash('Organ donation recorded successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error recording donation: {str(e)}', 'danger')
    finally:
        cursor.close()
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

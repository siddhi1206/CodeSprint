from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os
from functools import wraps

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


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


# Donor Management Routes
@app.route('/donors')
@login_required
def donors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM donor')
    donors = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('donors.html', donors=donors)


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

@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')


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
@app.route('/organ_matching', methods=['GET', 'POST'])
@login_required
def organ_matching():
    matches = []

    if request.method == 'POST':
        blood_group = request.form['blood_group']
        organ_type = request.form['organ_type']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Find matching recipients based on blood group and organ needed
        cursor.execute('''
            SELECT * FROM recipient 
            WHERE blood_group = %s AND organ_needed = %s AND status = 'Waiting'
        ''', (blood_group, organ_type))

        matches = cursor.fetchall()
        cursor.close()
        conn.close()

    return render_template('organ_matching.html', matches=matches)


@app.route('/record_donation', methods=['POST'])
@login_required
def record_donation():
    donor_id = request.form['donor_id']
    recipient_id = request.form['recipient_id']

    conn = get_db_connection()
    cursor = conn.cursor()

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
    cursor.close()
    conn.close()

    flash('Organ donation recorded successfully', 'success')
    return redirect(url_for('organ_matching'))


if __name__ == '__main__':
    app.run(debug=True)
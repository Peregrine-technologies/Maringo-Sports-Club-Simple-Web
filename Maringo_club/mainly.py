from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")

# Enable CSRF Protection
csrf = CSRFProtect(app)

# Connect to SQLite DB
def get_db_connection():
    conn = sqlite3.connect(os.getenv("DATABASE", "your_database.db"))
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
@app.route('/index.html')
def home():
    if 'logged_in' not in session or not session['logged_in']:
        flash('You must be logged in to view the home page.', 'info')
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['username'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register_user'))

        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if existing_user:
            flash('Username already taken.', 'danger')
            conn.close()
            return redirect(url_for('register_user'))

        # Hash the password before saving
        hashed_password = generate_password_hash(password)

        conn.execute('INSERT INTO users (first_name, last_name, username, email, password) VALUES (?, ?, ?, ?, ?)',
                     (first_name, last_name, username, email, hashed_password))
        conn.commit()
        conn.close()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/game_registration', methods=['GET', 'POST'])
@app.route('/games_registration.html', methods=['GET', 'POST'])
def game_registration():
    if request.method == 'POST':
        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'dob': request.form['dob'],
            'sport': request.form['sport'],
            'gender': request.form['gender'],
            'kin': request.form['kin'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'county': request.form['county'],
            'height': request.form['height'],
            'weight': request.form['weight'],
            'special_needs': request.form.get('special_needs', 'None'),
            'enrolment': request.form['enrolment']
        }

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO registrations (
                first_name, last_name, dob, sport, gender, kin, email, phone, county,
                height, weight, special_needs, enrolment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(data.values()))
        conn.commit()
        conn.close()
        flash('Registration successful! Thank you.', 'success')
        return redirect(url_for('home'))

    return render_template('games_registration.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'logged_in' not in session or not session['logged_in']:
        flash('Please log in to access the dashboard.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    regs = conn.execute('SELECT * FROM registrations').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', registrations=regs)

@app.route('/edit_registration/<int:id>', methods=['GET', 'POST'])
def edit_registration(id):
    if 'logged_in' not in session or not session['logged_in']:
        flash('Please log in to access this feature.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    reg = conn.execute('SELECT * FROM registrations WHERE id = ?', (id,)).fetchone()

    if not reg:
        flash('Registration not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        conn.execute('''
            UPDATE registrations SET
                first_name = ?, last_name = ?, dob = ?, sport = ?, gender = ?, kin = ?,
                email = ?, phone = ?, county = ?, height = ?, weight = ?, special_needs = ?, enrolment = ?
            WHERE id = ?
        ''', (
            request.form['first_name'], request.form['last_name'], request.form['dob'],
            request.form['sport'], request.form['gender'], request.form['kin'],
            request.form['email'], request.form['phone'], request.form['county'],
            request.form['height'], request.form['weight'], request.form['special_needs'],
            request.form['enrolment'], id
        ))
        conn.commit()
        conn.close()
        flash('Registration updated successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_registration.html', reg=reg)

@app.route('/delete_registration/<int:id>', methods=['POST'])
def delete_registration(id):
    if 'logged_in' not in session or not session['logged_in']:
        flash('Please log in to access this feature.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM registrations WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Registration deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/Facilitation_fee.html', methods=['GET', 'POST'])
def facilitation_fee():
    if request.method == 'POST':
        sport = request.form['sportEvent']
        team_size = int(request.form['teamSize'])
        patron_name = request.form['patronName']
        fee_per_person = 100
        total_fee = team_size * fee_per_person
        flash(f"Facilitation fee for {patron_name}'s {sport} event (Team Size: {team_size}) is KSh {total_fee:,}.", 'success')
        return redirect(url_for('facilitation_fee'))

    return render_template('Facilitation_fee.html')

@app.route('/purchase.html')
def purchase_item():
    return render_template('purchase.html')

@app.route('/sports_maintenance.html')
def sports_maintenance():
    return render_template('sports_maintenance.html')

@app.route('/store_items.html')
def store_items_management():
    return render_template('store_items.html')

@app.route('/contact_us.html', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        flash('Thank you for your message! We will get back to you shortly.', 'success')
        return redirect(url_for('contact_us'))
    return render_template('contact_us.html')

@app.route('/auth/google')
def google_auth():
    flash('Google authentication is not yet implemented.', 'info')
    return redirect(url_for('login'))

@app.route('/forgot_password')
def forgot_password():
    flash('Forgot password functionality is not yet implemented.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    if not os.path.exists('static/css'):
        os.makedirs('static/css')
    if not os.path.exists('static/css/styles.css'):
        with open('static/css/styles.css', 'w') as f:
            f.write("/* Add your custom styles here */")

    app.run(debug=True)

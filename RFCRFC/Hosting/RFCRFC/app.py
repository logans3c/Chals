import re
import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import secrets
import html
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SESSION_COOKIE_HTTPONLY'] = False

# Email validation regex rfc according to RFC 5322
EMAIL_REGEX = r'^(?!\.)("([^"\\]|\\.)*"|[-a-zA-Z0-9!#$%&\'*+/=?^_`{|}~]+(\.[-a-zA-Z0-9!#$%&\'*+/=?^_`{|}~]+)*)@(?!-)([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$'

# Database initialization
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            note TEXT NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    # Add a default admin if none exists
    c.execute("SELECT COUNT(*) FROM admins")
    if c.fetchone()[0] == 0:
        admin_password = os.environ.get('ADMIN_PASSWORD', 'default_secure_password')
        c.execute("INSERT INTO admins (username, password) VALUES (?, ?)", 
                  ('admin', admin_password))
    conn.commit()
    conn.close()

init_db()

# Helper function to generate application ID
def generate_app_id():
    return 'APP-' + secrets.token_hex(6).upper()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    note = request.form.get('note')
    
    # Validate email
    if not re.match(EMAIL_REGEX, email):
        flash('Invalid email format')
        return redirect(url_for('index'))
    
    # Generate a unique application ID
    app_id = generate_app_id()
    
    # Store in database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO applications (id, email, note) VALUES (?, ?, ?)",
              (app_id, email, note))
    conn.commit()
    conn.close()
    
    return render_template('confirmation.html', app_id=app_id)

def is_admin():
    """Check if current user is admin via session or FLAG cookie"""
    if session.get('admin'):
        return True
    
    # Also allow admin access if FLAG cookie matches environment variable
    flag_cookie = request.cookies.get('FLAG')
    env_flag = os.environ.get('FLAG')
    if flag_cookie and env_flag and flag_cookie == env_flag:
        return True
        
    return False


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM admins WHERE username = ? AND password = ?",
                  (username, password))
        admin = c.fetchone()
        conn.close()
        
        if admin:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid credentials')
    
    return render_template('admin_login.html')

@app.route('/admin')
def admin_panel():
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, email, note, status FROM applications")
    applications = [{'id': row[0], 'email': row[1], 
                    'note': row[2], 'status': row[3]} for row in c.fetchall()]
    conn.close()
    
    return render_template('admin.html', applications=applications)

@app.route('/admin/review/<app_id>', methods=['GET', 'POST'])
def review_application(app_id):
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        status = request.form.get('status')
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("UPDATE applications SET status = ? WHERE id = ?",
                  (status, app_id))
        conn.commit()
        conn.close()
        
        flash(f'Application {app_id} has been updated')
        return redirect(url_for('admin_panel'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, email, note, status FROM applications WHERE id = ?", (app_id,))
    application = c.fetchone()
    conn.close()
    
    if not application:
        flash('Application not found')
        return redirect(url_for('admin_panel'))
    
    app_data = {
        'id': application[0],
        'email': application[1],
        'note': application[2],
        'status': application[3]
    }
    
    return render_template('review.html', application=app_data)

# Updated bot endpoint to interface with the ctfbot service
@app.route('/bot', methods=['GET', 'POST'])
def bot():
    if request.method == 'POST':
        app_id = request.form.get('app_id')
        report_to_admin = request.form.get('report_to_admin')
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT id, email, note, status FROM applications WHERE id = ?", (app_id,))
        application = c.fetchone()
        conn.close()
        
        if not application:
            flash('Application not found')
            return render_template('bot.html')
        
        status_message = f"Your application (ID: {app_id}) is currently: {application[3]}"
        
        # If user wants to report to admin bot, send request to ctfbot
        if report_to_admin and report_to_admin == 'yes':
            try:
                # Create a URL that the admin bot will visit to review this application
                review_url = f"http://127.0.0.1:5000/admin/review/{app_id}"
                ctfbot_url = "http://localhost:3000/visit"
                
                # Send request to ctfbot to visit the review page
                response = requests.post(
                    ctfbot_url, 
                    json={"url": review_url},
                    timeout=30
                )
                
                if response.status_code == 200:
                    flash('Your application has been reported to the admin bot for review')
                else:
                    flash('Failed to contact admin bot')
            except requests.exceptions.RequestException:
                flash('Error contacting admin bot')
        
        return render_template('bot.html', status_message=status_message, app_id=app_id)
    
    return render_template('bot.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)

from flask import Flask, request, jsonify, make_response, redirect, render_template_string, render_template, flash, get_flashed_messages # Modified import
import jwt
import sqlite3
import os
import hashlib
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SESSION_COOKIE_NAME'] = 'flask_session'

# Load secret key from a configuration file
with open('app_config/.app_key') as f:
    JWT_SECRET = f.read().strip()

# Set secret key for Flask session/flash messages
app.secret_key = JWT_SECRET

# Read the salt from environment variable
PASSWORD_SALT = os.environ.get('PASSWORD_SALT', '')
print(f"Password salt initialized (length: {len(PASSWORD_SALT)})")

DB_PATH = 'data/appdata.db'
THUMBNAIL_DIR = 'static/thumbs' # Define thumbnail directory constant

os.makedirs('app_config', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True) # Use constant

# Memory store for active sessions (by username)
active_sessions = {'admin'}  # admin always active

@app.before_request
def session_check():
    # Skip auth check for these routes
    safe_routes = ['/access', '/signup', '/assets']
    if any(request.path.startswith(p) for p in safe_routes):
        return

    # Check if session cookie exists
    token = request.cookies.get('session')
    if not token:
        print("No session token found, redirecting to login")
        return redirect('/access')
    
    try:
        # Verify and decode the token
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        username = payload.get('username')

        # 1) ensure token in DB under this user
        with sqlite3.connect(DB_PATH) as db:
            cur = db.cursor()
            cur.execute("SELECT 1 FROM sessions WHERE token = ? AND username = ?", (token, username))
            if not cur.fetchone():
                print("Session token not found in DB for", username)
                return redirect('/access')

        # 2) ensure username is active
        if username not in active_sessions:
            print("Session not active for", username)
            return redirect('/access')

        # Attach user data to the request
        request.user = payload
        print(f"Valid session for user: {username}")
        
    except Exception as e:
        print(f"Session validation failed: {str(e)}")
        return redirect('/access')

@app.route('/')
def index():
    with sqlite3.connect(DB_PATH) as db:
        cur = db.cursor()

        # 1) fetch up to 5 feedbacks starting with "good"
        cur.execute(
            "SELECT entry "
            "  FROM feedback "
            " WHERE entry LIKE '%good%' "
            " ORDER BY LENGTH(entry) DESC "
            " LIMIT 5"
        )
        rows = cur.fetchall()

        if rows:
            # 2) pick the first entry without "bad"
            good = None
            for (entry,) in rows:
                if "bad" not in entry:
                    good = entry
                    break

            # 3) if none clean, fallback to the first and update it
            if not good:
                good = rows[0][0]
                print(good)
                cur.executescript(
                    f"UPDATE feedback "
                    f"   SET entry = 'good, perfect' "
                    f" WHERE entry = '{good}'"
                )
                db.commit()
                cur.execute(
                    "SELECT entry "
                    "  FROM feedback "
                    " WHERE entry = 'good, perfect' "
                )
                result  = cur.fetchone()
                if result:
                    good = result[0]

                # yes, it's a bit of a hack, but we are soo perfect.
            
            # sent latest feedbacks as one string

            latest_feedbacks = [good] if good else []
        else:
            latest_feedbacks = []

    return render_template("index.html",
                           user=request.user,
                           latest_feedbacks=latest_feedbacks) # Changed to render_template

@app.route('/entries')
def entries():
    username = request.user['username']
    with sqlite3.connect(DB_PATH) as db:
        cur = db.cursor()
        cur.execute("SELECT body, thumb FROM entries WHERE owner = ?", (username,))
        results = cur.fetchall()
    return render_template("entries.html", results=results, user=username) # Changed to render_template

@app.route('/new', methods=['POST'])
def new():
    content = request.form['note']
    thumb_filename = request.form.get('thumb_filename', '').strip()
    username = request.user['username']

    final_thumb_value = ''
    if thumb_filename:
        # remove ..
        safe_filename = thumb_filename.replace('..', '')
        print(f"Safe filename: {safe_filename}")
        if safe_filename:
             final_thumb_value = safe_filename
        else:
             flash("Invalid thumbnail filename provided.", "error")

             pass

    with sqlite3.connect(DB_PATH) as db:
        cur = db.cursor()
        # Store only the safe filename (or empty string) in the database
        cur.execute("INSERT INTO entries (owner, body, thumb) VALUES (?, ?, ?)", (username, content, final_thumb_value))
        db.commit()
    flash("New entry added successfully.", "success")
    return redirect('/entries')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        # Basic validation for username
        if not username or not username.isalnum():
             flash("Invalid Username. Use only letters and numbers.", "error")
             return render_template("signup.html")
        
        salted_pwd = PASSWORD_SALT + request.form['pwd']
        pwd = hashlib.sha256(salted_pwd.encode()).hexdigest()
        try:
            with sqlite3.connect(DB_PATH) as db:
                cur = db.cursor()
                # Check if user already exists
                cur.execute("SELECT 1 FROM users WHERE username = ?", (username,))
                if cur.fetchone():
                    flash("Username already exists. Please choose another or login.", "error")
                    return render_template("signup.html")
                # Insert new user
                cur.execute("INSERT INTO users (username, pwd, role) VALUES (?, ?, 'user')", (username, pwd))
                db.commit()
            flash("Signup successful! Please login.", "success")
            return redirect('/access')
        except sqlite3.IntegrityError: 
             flash("An error occurred during signup. Please try again.", "error")
             return render_template("signup.html")
        except Exception as e:
             app.logger.error(f"Signup error: {e}") # Log the error
             flash("An unexpected error occurred. Please try again later.", "error")
             return render_template("signup.html")

    return render_template("signup.html") # Changed to render_template

@app.route('/access', methods=['GET', 'POST'])
def access():
    if request.method == 'POST':
        username = request.form['username']
        if username in active_sessions:
            flash("User already has an active session. Please logout first.", "error")
            return render_template("access.html")
        salted_pwd = PASSWORD_SALT + request.form['pwd']
        pwd = hashlib.sha256(salted_pwd.encode()).hexdigest()

        print(f"Login attempt for user: {username}")

        try:
            with sqlite3.connect(DB_PATH) as db:
                cur = db.cursor()
                cur.execute("SELECT role FROM users WHERE username = ? AND pwd = ?", (username, pwd))
                row = cur.fetchone()
                
                if not row:
                    print(f"Invalid credentials for user: {username}")
                    flash("Invalid credentials. Please try again.", "error")
                    return render_template("access.html")  # Stay on login page

                role = row[0]
                print(f"Valid credentials for user: {username}, role: {role}")
                
                # CHECK if there's already a token for this user
                cur.execute("SELECT token FROM sessions WHERE username = ?", (username,))
                existing_token = cur.fetchone()
                
                if existing_token:
                    # Reuse existing token
                    token = existing_token[0]
                    print(f"Reusing existing token for {username}")
                else:
                    # Create a new token
                    payload = {
                        'username': username,
                        'role': role,
                        'exp': int((datetime.utcnow() + timedelta(days=1)).timestamp())
                    }
                    
                    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
                    if isinstance(token, bytes):
                        token = token.decode('utf-8')
                        
                    print(f"Generated new token for {username}")
                    
                    with sqlite3.connect(DB_PATH) as db2:
                        c2 = db2.cursor()
                        c2.execute(
                            "INSERT INTO sessions (username, token) VALUES (?, ?)",
                            (username, token)
                        )
                        db2.commit()
                
                active_sessions.add(username)

                # Create response with cookie
                resp = make_response(redirect('/'))
                resp.set_cookie(
                    'session', 
                    token, 
                    max_age=86400,  # 1 day in seconds
                    path='/'
                )
                
                print(f"Login successful for {username}. Redirecting to dashboard.")
                return resp
                
        except Exception as e:
            print(f"ERROR during login: {str(e)}")
            flash("An error occurred during login. Please try again.", "error")
    
    # For GET requests or failed logins
    return render_template("access.html")

@app.route('/logout')
def logout():
    token = request.cookies.get('session')
    if token:
        # decode token to find user
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user = payload.get('username')
        except:
            user = None
            
        if user and user != 'admin' and user in active_sessions:
            active_sessions.remove(user)
            
    resp = make_response(redirect('/access'))
    resp.set_cookie('session', '', expires=0, path='/')
    return resp

def get_available_thumbnails():
    """Get a list of all available thumbnails in the thumbnails directory"""
    try:
        thumbnails = []
        for file in os.listdir(THUMBNAIL_DIR):
            if file.endswith(('.jpg', '.jpeg', '.png', '.gif','avif')):
                thumbnails.append(file)
        return thumbnails
    except Exception as e:
        app.logger.error(f"Error listing thumbnails: {e}")
        return ['no_thumb.jpg']  # Fallback to at least one thumbnail

@app.route('/thumbnails')
def list_thumbnails():
    """Return a JSON list of available thumbnails"""
    thumbnails = get_available_thumbnails()
    return render_template("thumbnail_gallery.html", 
                          thumbnails=thumbnails,
                          user=request.user)

@app.route('/thumbnail')
def thumbnail():
    # Get the filename from the path parameter
    filename = request.args.get('path')
    if not filename:
        return "Missing filename", 400

    safe_filename = filename # we already secured the filename in the new() function
    if not safe_filename :
         return "Invalid filename", 400

    full_path = os.path.join(THUMBNAIL_DIR, safe_filename)


    try:
        # Use the constructed full path
        print(f"Loading thumbnail from {full_path}")
        with open(full_path, 'rb') as f:
            return f.read(), 200, {'Content-Type': 'image/jpeg'}
    except FileNotFoundError:
         return "Thumbnail not found", 404
    except Exception as e:
        app.logger.error(f"Thumbnail error for {full_path}: {e}")
        return f"Error loading thumbnail", 500

@app.route('/feedback', methods=['POST'])
def feedback():
    entry = request.form['entry']
    username = request.user['username']
    with sqlite3.connect(DB_PATH) as db:
        cur = db.cursor()
        cur.execute(
            "INSERT INTO feedback (username, entry) VALUES (?, ?)",
            (username, entry)
        )
        db.commit()
    return redirect('/?feedback=sent') 

@app.route('/flag')
def flag():
    username = request.user['username']
    
    # 1. Check if the role in JWT is 'admin'
    jwt_role = request.user.get('role')
    if jwt_role != 'admin':
        return render_template("flag.html", 
                              user=request.user,
                              flag="You don't have permission to view the flag. JWT role is not admin.")
    
    # 2. Double-check the user's role directly from the database
    with sqlite3.connect(DB_PATH) as db:
        cur = db.cursor()
        # Verify the user's actual role in the database
        cur.execute("SELECT role FROM users WHERE username = ?", (username,))
        result = cur.fetchone()
        
        if not result or result[0] != 'admin':
            return render_template("flag.html", 
                                  user=request.user,
                                  flag="You don't have permission to view the flag. Database role is not admin.")
        
        # 3. User is confirmed admin in both JWT and database
        flag = os.environ.get('APP_FLAG', "Error: Flag not configured")
        
        return render_template("flag.html",
                              user=request.user,
                              flag=flag)

def ensure_admin_exists():
    try:
        with sqlite3.connect(DB_PATH) as db:
            cur = db.cursor()
            # Check if admin user exists
            cur.execute("SELECT 1 FROM users WHERE username = 'admin'")
            if not cur.fetchone():
                # Add admin user if it doesn't exist
                salted_pwd = PASSWORD_SALT + 'supersecure'
                cur.execute("INSERT INTO users (username, pwd, role) VALUES ('admin', ?, 'admin')", 
                           (hashlib.sha256(salted_pwd.encode()).hexdigest(),))
            # ensure admin session exists
            payload = {
                'username': 'admin',
                'role': 'admin',
                'exp': int((datetime.utcnow() + timedelta(days=1)).timestamp())
            }
            token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
            if isinstance(token, bytes):
                token = token.decode('utf-8')
            # upsert into sessions
            cur.execute("DELETE FROM sessions WHERE username = 'admin'")
            cur.execute("INSERT INTO sessions (username, token) VALUES ('admin', ?)", (token,))
            db.commit()
        active_sessions.add('admin')
    except Exception as e:
        print(f"ERROR ensuring admin session: {e}")

# Database and Key Initialization
if not os.path.exists(DB_PATH):
    print(f"Database not found at {DB_PATH}. Initializing...")
    try:
        with sqlite3.connect(DB_PATH) as db:
            cur = db.cursor()
            cur.execute("CREATE TABLE users (username TEXT PRIMARY KEY, pwd TEXT, role TEXT)")
            cur.execute("CREATE TABLE entries (id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT, body TEXT, thumb TEXT)")
            cur.execute(
                "CREATE TABLE sessions ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "username TEXT, "
                "token TEXT, "
                "created DATETIME DEFAULT CURRENT_TIMESTAMP)"
            )
            cur.execute(
                "CREATE TABLE feedback ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "username TEXT, "
                "entry TEXT, "
                "timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"
            )
            # Add admin user
            salted_admin_pwd = PASSWORD_SALT + 'supersecure'
            cur.execute("INSERT INTO users VALUES ('admin', ?, 'admin')", 
           (hashlib.sha256(salted_admin_pwd.encode()).hexdigest(),))

            # Add initial entry for admin user - store only filename
            cur.execute("INSERT INTO entries (owner, body, thumb) VALUES ('admin', 'Welcome admin!', 'admin_default.jpg')")
            db.commit()
        print("Database initialized with admin user and initial entry.")
        # generate & store admin JWT
        payload = {
            'username': 'admin',
            'role': 'admin',
            'exp': int((datetime.utcnow() + timedelta(days=1)).timestamp())
        }
        admin_token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        if isinstance(admin_token, bytes):
            admin_token = admin_token.decode('utf-8')
        with sqlite3.connect(DB_PATH) as db:
            c = db.cursor()
            c.execute("INSERT INTO sessions (username, token) VALUES ('admin', ?)", (admin_token,))
            db.commit()
        active_sessions.add('admin')
        default_thumb_path = os.path.join(THUMBNAIL_DIR, 'admin_default.jpg')
        if not os.path.exists(default_thumb_path):
             try:
                 with open(default_thumb_path, 'w') as f:
                     f.write("dummy jpeg data") 
                 print(f"Created dummy default thumbnail at {default_thumb_path}")
             except IOError as e:
                 print(f"Warning: Could not create dummy thumbnail {default_thumb_path}: {e}")
    except Exception as e:
        print(f"ERROR: Failed to initialize database at {DB_PATH}: {e}")
        exit(1)
else:
    print(f"Database found at {DB_PATH}.")
    ensure_admin_exists()

if __name__ == '__main__':
    # Run on 0.0.0.0 to be accessible outside the container
    app.run(host='0.0.0.0', port=5000)


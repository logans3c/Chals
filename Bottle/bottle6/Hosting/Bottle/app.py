from bottle import Bottle, run, template, request, redirect, response, static_file, error
import os
import hashlib
import hmac
import base64
import time
from bottle import TEMPLATE_PATH
import uuid
import requests  # Add this import
import socket
TEMPLATE_PATH.append(os.path.join(os.path.dirname(__file__), 'views'))

app = Bottle()

class RemoveProxyHeadersMiddleware:
    def __init__(self, app):
        self.wrapped_app = app
        
    def __call__(self, environ, start_response):
        # Remove any proxy-related headers
        headers_to_remove = [
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_REAL_IP',
            'HTTP_CF_CONNECTING_IP',
            'HTTP_X_FORWARDED_PROTO',
            'HTTP_X_FORWARDED_HOST'
        ]
        
        for header in headers_to_remove:
            if header in environ:
                del environ[header]
                
        return self.wrapped_app(environ, start_response)

# In-memory storage
users = {}
users['admin'] = hashlib.sha256('adminws'.encode()).hexdigest()
notes = {}
sessions = {}
admin_credentials = {'admin': 'adminws'}  # admin credentials
SECRET_KEY = 'pwdpwdpwdpwdpwd'  # Used for signing cookies

# Helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_authenticated(session_id):
    return session_id in sessions

def get_user_from_session(session_id):
    return sessions.get(session_id)

# Custom cookie signing and verification functions
def sign_data(data, secret=SECRET_KEY):
    """Create a signature for the given data using HMAC"""
    if not isinstance(data, bytes):
        data = str(data).encode('utf-8')
    
    # Create an HMAC signature
    digest = hmac.new(secret.encode('utf-8'), data, hashlib.sha256).digest()
    signature = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    return signature

def create_signed_value(data, secret=SECRET_KEY):
    """Create a signed cookie value: data|timestamp|signature"""
    timestamp = str(int(time.time()))
    signature = sign_data(data + timestamp, secret)
    # Format: value|timestamp|signature
    return f"{data}|{timestamp}|{signature}"

def decode_signed_value(signed_value, secret=SECRET_KEY, max_age=None):
    """Verify and extract the original value from a signed cookie"""
    if not signed_value:
        return None
    
    # Split the parts
    parts = signed_value.split('|')
    if len(parts) != 3:
        return None
    
    value, timestamp, signature = parts
    
    # Check timestamp if max_age is specified
    if max_age:
        try:
            timestamp_int = int(timestamp)
            if int(time.time()) - timestamp_int > max_age:
                return None  # Cookie has expired
        except ValueError:
            return None  # Invalid timestamp
    
    # Verify signature
    expected_sig = sign_data(value + timestamp, secret)
    if not hmac.compare_digest(expected_sig, signature):
        return None  # Invalid signature
    
    return value

# Custom cookie functions without quotes
def set_custom_cookie(response_obj, name, value, signed=False, **kwargs):
    """Set a cookie without quotes, optionally signing it"""
    # Handle signing if requested
    if signed:
        secret = kwargs.pop('secret', SECRET_KEY)
        value = create_signed_value(value, secret)
    
    # Build cookie string parts
    path = kwargs.get('path', '/')
    domain = kwargs.get('domain', None)
    max_age = kwargs.get('max_age', None)
    expires = kwargs.get('expires', None)
    httponly = kwargs.get('httponly', False)
    secure = kwargs.get('secure', False)
    samesite = kwargs.get('samesite', None)
    
    # Build cookie string
    cookie_parts = [f"{name}={value}"]
    if domain:
        cookie_parts.append(f"Domain={domain}")
    if path:
        cookie_parts.append(f"Path={path}")
    if max_age:
        cookie_parts.append(f"Max-Age={max_age}")
    if expires:
        cookie_parts.append(f"Expires={expires}")
    if secure:
        cookie_parts.append("Secure")
    if httponly:
        cookie_parts.append("HttpOnly")
    if samesite:
        cookie_parts.append(f"SameSite={samesite}")
    
    cookie_header = "; ".join(cookie_parts)
    
    # Set the cookie header directly
    response_obj.add_header('Set-Cookie', cookie_header)
    return response_obj

def get_custom_cookie(name, default=None, signed=False, secret=SECRET_KEY, max_age=None):
    """Get a cookie value, optionally verifying signature"""
    value = request.get_cookie(name, default)
    if not value or not signed:
        return value
    
    # Verify and decode the signed value
    return decode_signed_value(value, secret, max_age)

def get_lang():
    """Get the language from cookie"""
    lang = get_custom_cookie('lang')
    if not lang:
        lang = 'en'
    return lang

@app.route('/set-lang/<lang>')
def set_lang(lang):
    set_custom_cookie(response, 'lang', lang, path='/', httponly=False)
    redirect(request.headers.get('Referer') or '/')

# Routes
@app.route('/')
def index():
    lang = get_lang()
    # If lang cookie is not set, set it to default value 'en'
    if not get_custom_cookie('lang'):
        set_custom_cookie(response, 'lang', 'en', path='/', httponly=False)
        lang = 'en'
    return template('index.tpl', lang=lang)

@app.route('/register', method=['GET', 'POST'])
def register():
    message = ''
    lang = get_lang()
    success = False
    if request.method == 'POST':
        username = request.forms.get('username')
        password = request.forms.get('password')
        if not username or not password:
            message = 'Username and password are required.'
        elif username in users:
            message = 'Username already exists.'
        else:
            users[username] = hash_password(password)
            message = 'Registration successful! Please log in.'
            success = True
            return template('register.tpl', message=message, success=success, lang=lang)
    return template('register.tpl', message=message, success=success, lang=lang)

@app.route('/login', method=['GET', 'POST'])
def login():
    message = ''
    lang = get_lang()
    if request.method == 'POST':
        username = request.forms.get('username')
        password = request.forms.get('password')
        if not username or not password:
            message = 'Username and password are required.'
        elif username in users and users[username] == hash_password(password):
            session_id = os.urandom(16).hex()
            sessions[session_id] = username
            # Set a signed session cookie
            set_custom_cookie(response, 'session', session_id, signed=True, httponly=True, path='/')
            # Set language cookie (not signed)
            set_custom_cookie(response, 'lang', lang, path='/', httponly=False)
            redirect('/note/add-note')
        else:
            message = 'Invalid username or password.'
    return template('login.tpl', message=message, lang=lang)

@app.route('/note/add-note', method=['GET', 'POST'])
def add_note():
    # Get and verify the signed session cookie
    session_id = get_custom_cookie('session', signed=True, max_age=86400)  # 24 hour max age
    if not is_authenticated(session_id):
        redirect('/login')
    
    username = get_user_from_session(session_id)
    message = ''
    success = False
    lang = get_lang()
    if request.method == 'POST':
        note_content = request.forms.get('note')
        if not note_content or not note_content.strip():
            message = 'Note content cannot be empty.'
        else:
            if username not in notes:
                notes[username] = []
            note_id = str(uuid.uuid4())
            notes[username].append({'id': note_id, 'content': note_content})
            message = 'Note added successfully.'
            success = True
    
    user_notes = notes.get(username, [])
    return template('add_note.tpl', notes=user_notes, message=message, success=success, lang=lang)

@app.route('/note/<note_id>')
def preview_note(note_id):
    session_id = get_custom_cookie('session', signed=True)
    if not is_authenticated(session_id):
        redirect('/login')
    username = get_user_from_session(session_id)
    lang = get_lang()
    note = None
    if username == 'admin':
        # Admin can access any note
        for user_notes in notes.values():
            for n in user_notes:
                if n['id'] == note_id:
                    note = n
                    break
            if note:
                break
    else:
        user_notes = notes.get(username, [])
        note = next((n for n in user_notes if n['id'] == note_id), None)
    if not note:
        # Return a plain error message, not as a template
        return '<div style="color:red;">Note not found.</div>'
    return template('note_preview.tpl', note=note, lang=lang)


@app.route('/about')
def about():
    lang = get_lang()
    print("Sessions:", sessions)
    return template('about.tpl', lang=lang)

@app.route('/admin-login', method=['GET', 'POST'])
def admin_login():
    lang = get_lang()
    print("Admin login page accessed")
    print("Sessions:", sessions)
    if request.method == 'POST':
        username = request.forms.get('username')
        password = request.forms.get('password')
        if username in admin_credentials and admin_credentials[username] == password:
            session_id = os.urandom(16).hex()
            sessions[session_id] = 'admin'
            # Set a signed session cookie
            set_custom_cookie(response, 'session', session_id, signed=True, httponly=True, path='/')
            # Set language cookie (not signed)
            set_custom_cookie(response, 'lang', lang, path='/', httponly=False)
            redirect('/admin')
    return template('admin_login.tpl', lang=lang)

@app.route('/admin')
def admin_dashboard():
    session_id = get_custom_cookie('session', signed=True)
    lang = get_lang()
    if not is_authenticated(session_id) or get_user_from_session(session_id) != 'admin':
        redirect('/admin-login')
    return template('admin_dashboard.tpl', lang=lang)

@app.route('/admin/flag')
def admin_flag():
    session_id = get_custom_cookie('session', signed=True)
    # Check admin authentication
    if not is_authenticated(session_id) or get_user_from_session(session_id) != 'admin':
        redirect('/admin-login')
    real_ip = request.remote_addr
    print(f"Real IP: {real_ip}")
        # Block localhost IPs directly without relying on hostname lookup
    if real_ip == '127.0.0.1' or real_ip == '::1' or real_ip.startswith('127.'):
        return "Access denied from localhost."
    try:
        hostname = socket.gethostbyaddr(real_ip)[0]
        print(f"Resolved hostname: {hostname}")
    except Exception as e:
        hostname = ""
        print(f"Hostname lookup failed: {e}")
    if 'localhost' in hostname:
        return "Access denied."
    # GET THE FLAG FROM DF OR READ IT FROM flag.txt
    flag = os.environ.get('DF', '{Flag not set}') or open('flag.txt').read().strip()

    print(f"Flag retrieved: {flag}")
    return template('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Admin Flag</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <div class="container">
                <h1>Admin Flag</h1>
                <div style="margin: 20px 0; color: #222; font-size: 1.2em;">
                    {{flag}}
                </div>
                <a href="/admin">Back to Admin Dashboard</a>
            </div>
        </body>
        </html>
    ''', flag=flag)

@app.route('/logout')
def logout():
    print("someone is logging out")
    # No need to verify signature for logout
    session_id = get_custom_cookie('session')
    if session_id in sessions:
        del sessions[session_id]
    # Use standard delete_cookie as we're removing, not setting
    response.delete_cookie('session', path='/')
    redirect('/login')

@app.route('/static/<filepath:path>')
def server_static(filepath):
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    return static_file(filepath, root=static_dir)

@app.route('/bot', method=['GET', 'POST'])
def report_to_bot():
    # No authentication/cookie required
    lang = get_lang()
    message = ''
    success = False
    if request.method == 'POST':
        note_id = request.forms.get('note_id')
        if not note_id:
            message = 'Note ID is required.'
        else:
            found = False
            for user_notes in notes.values():
                for note in user_notes:
                    if note['id'] == note_id:
                        found = True
                        break
                if found:
                    break
            if not found:
                message = 'Note not found.'
            else:
                note_url = f"http://127.0.0.1:8081/note/{note_id}"
                try:
                    # Make the request in a separate thread to avoid blocking
                    import threading
                    def send_to_bot():
                        requests.post("http://127.0.0.1:3000/", data={'url': note_url}, timeout=30)
                    
                    thread = threading.Thread(target=send_to_bot)
                    thread.daemon = True
                    thread.start()
                    
                    message = 'Note reported to admin bot successfully!'
                    success = True
                except Exception as e:
                    message = f'Error contacting bot: {e}'
    return template('report_bot.tpl', message=message, success=success, lang=lang)

@app.error(404)
def error404(error):
    return 'Page not found'

if __name__ == '__main__':
    # Apply middleware
    app_with_middleware = RemoveProxyHeadersMiddleware(app)
    run(app_with_middleware, host='0.0.0.0', port=8081, debug=True)


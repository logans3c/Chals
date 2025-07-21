from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bleach
from sqlalchemy import func, desc
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/auth/login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.relationship('Note', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Add this model for storing user notes
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Add a model for storing reported links
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(2000), nullable=False)
    description = db.Column(db.Text, nullable=True) # Ensures description is stored
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)
    reported_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, visited, failed

# Update User model with reports relationship
User.reports = db.relationship('Report', backref='reporter', lazy=True, foreign_keys='Report.reported_by')

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Update the bot route
@app.route('/bot', methods=['GET', 'POST'])
@login_required
def bot():
    result = None
    
    if request.method == 'POST':
        url = request.form.get('url', '')
        description = request.form.get('description', '') # Captures description
        
        if not url:
            flash('URL is required.')
            return redirect(url_for('bot'))
        
        # For security, make sure URL starts with http:// or https://
        if not url.startswith(('http://', 'https://')):
            flash('URL must start with http:// or https://')
            return redirect(url_for('bot'))
        
        # Store the report in the database
        try:
            # Create and save a new report
            report = Report(
                url=url,
                description=description, # Saves description
                reported_by=current_user.id
            )
            db.session.add(report)
            db.session.commit()
            
            import requests
            
            # Send the report to the bot service
            bot_url = 'http://localhost:3000/' 
            payload = {'url': url}
            
            try:
                response = requests.post(bot_url, data=payload, timeout=20)
                if response.status_code == 200:
                    result = {
                        'url': url,
                        'description': description,
                        'checked': True,
                        'result': "Your URL has been reported to the admin. The bot will visit it shortly."
                    }
                    flash('URL reported successfully!')
                else:
                    # Update report status to failed
                    report.status = 'failed'
                    db.session.commit()
                    
                    result = {
                        'url': url,
                        'description': description,
                        'checked': False,
                        'result': "Error: The bot service returned an error."
                    }
                    flash('Failed to report URL to the bot.')
            except Exception as e:
                result = {
                    'url': url,
                    'description': description,
                    'checked': False,
                    'result': f"Error: {str(e)}"
                }
                flash(f'Error connecting to bot service: {str(e)}')
                
        except Exception as e:
            flash(f'Error processing request: {str(e)}')
            return redirect(url_for('bot'))
    
    return render_template('bot.html', result=result)

# Add an admin-only view for reported links
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Only allow admin user to log in through this endpoint
        if username != 'admin':
            flash('Invalid username or password.')
            return render_template('admin_login.html')
            
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.')
            
    return render_template('admin_login.html')

@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    # Only allow admin to access this page
    if current_user.username != 'admin':
        abort(403)
        
    # Fetch all reported links for the admin to review
    reports = Report.query.order_by(Report.reported_at.desc()).all() # Fetches reports with descriptions
    
    return render_template('admin_dashboard.html', reports=reports)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth/<action>', methods=['GET', 'POST'])
def auth(action):
    if current_user.is_authenticated:
        match action:
            case 'logout':
                logout_user()
                flash('Logged out successfully.')
                return redirect(url_for('index'))
            case _:
                return redirect(url_for('index'))
    else:
        match action:
            case 'login':
                if request.method == 'POST':
                    username = request.form.get('username')
                    password = request.form.get('password')
                    
                    user = User.query.filter_by(username=username).first()
                    
                    if user and user.check_password(password):
                        login_user(user)
                        flash('Logged in successfully.')
                        return redirect(url_for('index'))
                    else:
                        flash('Invalid username or password.')
                
                return render_template('login.html')
                
            case 'register':
                if request.method == 'POST':
                    username = request.form.get('username')
                    email = request.form.get('email')
                    password = request.form.get('password')
                    confirm_password = request.form.get('confirm_password')
                    
                    if password != confirm_password:
                        flash('Passwords do not match.')
                        return render_template('register.html')
                        
                    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
                    
                    if existing_user:
                        flash('Username or email already exists.')
                        return render_template('register.html')
                    
                    user = User(username=username, email=email)
                    user.set_password(password)
                    
                    db.session.add(user)
                    db.session.commit()
                    
                    flash('Registration successful. Please log in.')
                    return redirect(url_for('auth', action='login'))
                
                return render_template('register.html')
                
            case _:
                return redirect(url_for('index'))

@app.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == 'POST':
        content = request.form.get('content', '')
        
        
        sanitized_content = bleach.clean(content)
        
        if not sanitized_content.strip():
            flash('Note content cannot be empty.')
            return redirect(url_for('notes'))
        
        note = Note(content=sanitized_content, user_id=current_user.id)
        
        db.session.add(note)
        db.session.commit()
        
        flash('Note added successfully!')
        return redirect(url_for('notes'))
    
    user_notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.created_at.desc()).all()
    return render_template('notes.html', notes=user_notes)

@app.route('/notes/delete/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    
    
    if note.user_id != current_user.id:
        abort(403)  # Forbidden
    
    db.session.delete(note)
    db.session.commit()
    
    flash('Note deleted successfully!')
    return redirect(url_for('notes'))

@app.route('/activity')
def user_activity():
    action = request.args.get('action', 'note_count')
    username = request.args.get('username')
    
    if not username:
        flash('Username is required.')
        return redirect(url_for('index'))
    
    # Use parameterized query to prevent SQL injection
    user = User.query.filter_by(username=username).first()
    
    if not user:
        flash('User not found.')
        return redirect(url_for('index'))
    
    # Common data for all actions
    note_count = Note.query.filter_by(user_id=user.id).count()
    
    # Calculate user rank based on note count
    user_ranks = db.session.query(
        User.id,
        func.rank().over(order_by=func.count(Note.id).desc()).label('rank')
    ).join(Note).group_by(User.id).all()
    
    user_rank = 0
    for rank_data in user_ranks:
        if rank_data[0] == user.id:
            user_rank = rank_data[1]
            break
    
    if user_rank == 0:
        user_rank = len(User.query.all())  # If user has no notes, they are last
    
    # Calculate total words written
    user_notes = Note.query.filter_by(user_id=user.id).all()
    total_words = sum(len(note.content.split()) for note in user_notes)
    
    # Calculate word count rank
    word_count_ranks = db.session.query(
        User.id,
        func.rank().over(
            order_by=desc(func.sum(func.length(Note.content) - 
                               func.length(func.replace(Note.content, ' ', '')) + 1))
        ).label('word_rank')
    ).join(Note).group_by(User.id).all()
    
    word_rank = 0
    for rank_data in word_count_ranks:
        if rank_data[0] == user.id:
            word_rank = rank_data[1]
            break
    
    if word_rank == 0:
        word_rank = len(User.query.all())  # If user has no words, they are last
    
    # Prepare template parameters
    template_params = {
        'username': username,
        'note_count': note_count,
        'rank': user_rank,
        'word_count': total_words,
        'word_rank': word_rank,
        'note_rank': user_rank
    }
    
    # Get the list of available activity templates
    activity_templates_dir = os.path.join(app.root_path, 'templates', 'activity')
    available_templates = [f.split('.')[0] for f in os.listdir(activity_templates_dir) ]

    template_name = f'activity/{action}'
    
    # Pass available templates list to the template
    template_params['available_activities'] = available_templates
    
    return render_template(template_name, **template_params)

@app.route('/top_users')
def top_users():
    # Get the top 3 users based on note count
    top_users = db.session.query(
        User.username,
        func.count(Note.id).label('note_count')
    ).join(Note).group_by(User.id).order_by(desc('note_count')).limit(3).all()
    
    return jsonify([{'username': username, 'note_count': note_count} for username, note_count in top_users])

@app.route('/profile')
@login_required
def profile():
    note_count = Note.query.filter_by(user_id=current_user.id).count()
    return render_template('profile.html', note_count=note_count)

with app.app_context():
    db.create_all() # Create database tables before first request

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)

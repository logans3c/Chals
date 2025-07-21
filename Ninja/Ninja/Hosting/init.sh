#!/bin/bash
set -e

echo "Starting initialization script..."

# Create admin user and add flag note
python3 - <<EOF
from app import app, db, User, Note
from werkzeug.security import generate_password_hash
import os

# Get admin password from environment variable or use default
admin_password = os.environ.get('ADMIN_PASSWORD', 'adminwwwwwwwwwwwwwwws')
flag = os.environ.get('DF', 'flag{j1nj4_x5s_0wn3d_y0u}')

with app.app_context():
    # Check if admin user already exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash(admin_password)
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully")
    else:
        print("Admin user already exists")
    
    # Check if admin already has a flag note
    flag_note = Note.query.filter_by(
        user_id=admin.id, 
        content=f"SECRET FLAG: {flag}"
    ).first()
    
    if not flag_note:
        print("Adding flag note to admin account...")
        flag_note = Note(
            content=f"SECRET FLAG: {flag}",
            user_id=admin.id
        )
        db.session.add(flag_note)
        db.session.commit()
        print("Flag note added successfully")
    else:
        print("Flag note already exists")
EOF

# Start the bot service in the background
echo "Starting bot service..."
cd /app/Bot/bot && NODE_ENV=production node index.js &
BOT_PID=$!

# Wait for bot service to start
sleep 3
echo "Bot service started with PID $BOT_PID"

# Start the Flask application
echo "Starting Flask application..."
cd /app
python3 app.py

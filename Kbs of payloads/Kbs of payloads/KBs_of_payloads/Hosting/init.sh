#!/bin/bash
set -e  # Exit on error

# Function definitions must come first
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

check_process() {
    pgrep -f "$1" >/dev/null
    return $?
}
generate_random_numbers() {
    # Generate 6 random numbers
    echo $(( RANDOM % 900000 + 100000 ))
}

# Set the flag
if [ -z "$DF" ]; then
    echo "FLAG{rush}" > /flag.txt
else
    echo $DF > /flag.txt
fi


# Start the Python application (Flask challenge)
log "Starting WAF application..."
sudo -u app bash -c "export FLASK_RUN_PORT=8000 \
                           FLASK_RUN_HOST=0.0.0.0 \
                           FLASK_APP=/home/app/waf/waf.py && \
                     cd /home/app/waf/ && \
                     flask run" &

sleep 2
if ! check_process "flask run"; then
    log "ERROR: WAF failed to start"
    exit 1
fi
log "WAF started successfully"


# Start the Node.js application (Preview)
log "Starting Node.js application..."
chmod 755 /home/app/preview
sudo -u app bash -c "export DF=\"$DF\" && cd /home/app/preview && nodemon run dev" &

sleep 2
# Initialize database with admin user
log "Initializing database..."
RANDOM_NUMBERS=$(generate_random_numbers)
ADMIN_EMAIL="${RANDOM_NUMBERS}@cybertalents.com"
ADMIN_PASSWORD="sunflower"
HASHED_PASSWORD=$(python3 -c "import bcrypt; print(bcrypt.hashpw(b'$ADMIN_PASSWORD', bcrypt.gensalt(8)).decode())")
# Create admin user in SQLite database
sqlite3 /home/app/preview/note_app.sqlite << EOF
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT 1 CHECK (is_admin = 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO admins (name, email, password, is_admin)
VALUES ('admin', '${ADMIN_EMAIL}', '${HASHED_PASSWORD}', 1);
EOF

if [ $? -eq 0 ]; then
    log "Database initialized successfully with admin user: ${ADMIN_EMAIL}"
else
    log "ERROR: Failed to initialize database"
    exit 1
fi

# Start Nginx with proper error checking
log "Starting Nginx..."
if ! nginx -t; then
    log "ERROR: Nginx configuration test failed"
    cat /var/log/nginx/error.log
    exit 1
fi

if ! service nginx start; then
    log "ERROR: Nginx failed to start"
    cat /var/log/nginx/error.log
    systemctl status nginx
    exit 1
fi

if ! service nginx status > /dev/null 2>&1; then
    log "ERROR: Nginx is not running"
    cat /var/log/nginx/error.log
    systemctl status nginx
    exit 1
fi

# Optionally run the validation script
sleep 5
# Keep the container running
tail -f /dev/null

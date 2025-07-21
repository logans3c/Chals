#!/bin/bash
# Check if the DF environment variable is set
if [ -z "$DF" ]; then
    # If DF is not set, write a default flag
    export APP_FLAG="flag{s3cond_0rd3r_SQLi_1s_tw1c3_as_d4ng3rous}"
else
    # If DF is set, write its value to the flag file
    export APP_FLAG="$DF"
fi
# Unset the DF variable to clean up the environment
unset DF

# Set up password salt
if [ -z "$SALT" ]; then
    # If SALT is not set, use this default salt (in production, use a random string)
    export PASSWORD_SALT="9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
else
    # If SALT is set, use the provided value
    export PASSWORD_SALT="$SALT"
fi

# Ensure app directories exist
mkdir -p /app/data
mkdir -p /app/static/thumbs
mkdir -p /app/templates

# Generate a random secret key if not present
if [ ! -f /app/app_config/.app_key ]; then
    python -c "import os; print(os.urandom(24).hex())" > /app/app_config/.app_key
fi

# Run the Flask app - the salt will be read once at startup
cd /app
python app.py &

sleep 5
# Unset the salt variable (though this won't affect the running app)
unset PASSWORD_SALT

chmod 777 post_init.sh
./post_init.sh

wait
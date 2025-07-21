#!/bin/bash

# Check if the DF environment variable is set
if [ -z "$DF" ]; then
    # If DF is not set, write a default flag
    # flag is xss in email is possible
    echo "flag{X55_1n_3m41l_15_p0551bl3}" > /root/flag.txt
else
    # If DF is set, write its value to the flag file
    echo "$DF" > /root/flag.txt
fi
# Unset the DF variable to clean up the environment
unset DF

# Read the flag contents to use as a cookie
export FLAG=$(cat /root/flag.txt)

export ADMIN_PASSWORD="adminnnnnnnnnnnnnnnnnn"

# Start the CTF bot service in the background
cd /app/ctfbot
node index.js &

# Wait for the bot to start
sleep 3

# Start the Flask application
cd /app
python app.py

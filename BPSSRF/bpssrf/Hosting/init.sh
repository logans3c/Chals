#!/bin/bash

# Set up the flag
if [ -z "$DF" ]; then
    # If DF is not set, write the default flag to flag.txt in the app's directory
    echo "flag{stigmata_stigmata_stigmata}" > /app/flag.txt
else
    # If DF is set, write its value to flag.txt
    echo "$DF" > /app/flag.txt
fi

# Start the Flask application
python3 /app/app.py
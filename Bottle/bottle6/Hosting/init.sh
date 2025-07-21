#!/bin/bash

# Check if the DF environment variable is set
if [ -z "$DF" ]; then
    # If DF is not set, write the default flag to flag.txt in the app's directory
    echo "flag{h0w_d1d_y0u_bypass_the_http0nly_flag}" > flag.txt
else
    # If DF is set, write its value to flag.txt
    echo "$DF" > flag.txt
fi
# Unset the DF variable to clean up the environment
unset DF

set -e

echo "Starting services..."

# Start the Bottle app
echo "Starting Bottle app..."
cd /app/bottle-note-app
python app.py &
BOTTLE_PID=$!

# Wait for Bottle to start
sleep 5

# Check if Bottle is running
if ! kill -0 $BOTTLE_PID 2>/dev/null; then
    echo "Bottle app failed to start"
    exit 1
fi

echo "Bottle app started successfully (PID: $BOTTLE_PID)"

# Start the bot app
echo "Starting bot app..."
cd /app/bot/bot
node index.js &
BOT_PID=$!

# Wait for bot to start
sleep 5

# Check if bot is running
if ! kill -0 $BOT_PID 2>/dev/null; then
    echo "Bot app failed to start"
    kill $BOTTLE_PID 2>/dev/null
    exit 1
fi

echo "Bot app started successfully (PID: $BOT_PID)"
echo "All services are running"

# Function to handle cleanup
cleanup() {
    echo "Shutting down services..."
    kill $BOTTLE_PID $BOT_PID 2>/dev/null || true
    wait $BOTTLE_PID $BOT_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Keep the container running by waiting for background processes
wait
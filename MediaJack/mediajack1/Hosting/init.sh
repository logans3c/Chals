#!/bin/bash
# Check if the DF environment variable is set
if [ -z "$DF" ]; then
    # If DF is not set, write a default flag
    echo "flag{p0llu73d_pr070_ffmp3g_pwn3d}" > /root/flag.txt
else
    # If DF is set, write its value to the flag file
    echo "$DF" > /root/flag.txt
fi
# Unset the DF variable to clean up the environment
unset DF

# Start the app with pm2 in watch mode
exec pm2-runtime start server.js

# To stop the app if started with pm2:
# pm2 stop server

# To stop all pm2 processes:
# pm2 stop all

# To delete the process from pm2 list:
# pm2 delete server

# If you started with pm2-runtime (as in Docker), just stop the container/process.

#!/bin/bash

# Keep Redaccel server running automatically
# This script will restart the server if it stops

cd "$(dirname "$0")"

while true; do
    if ! pgrep -f "python3 redaccel_app.py" > /dev/null; then
        echo "$(date): Starting Redaccel server..."
        python3 redaccel_app.py >> redaccel_server.log 2>&1 &
        sleep 2
    fi
    sleep 5
done

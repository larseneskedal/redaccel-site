#!/bin/bash

# Auto-start script for Redaccel website
# This script will start the server and keep it running

cd "$(dirname "$0")"

# Check if server is already running
if pgrep -f "python3 redaccel_app.py" > /dev/null; then
    echo "✅ Redaccel server is already running!"
    echo "📍 Access at: http://localhost:5002"
    exit 0
fi

# Start the server in the background
echo "🚀 Starting Redaccel server..."
nohup python3 redaccel_app.py > redaccel_server.log 2>&1 &

# Wait a moment for server to start
sleep 2

# Check if it started successfully
if pgrep -f "python3 redaccel_app.py" > /dev/null; then
    echo "✅ Server started successfully!"
    echo "📍 Access at: http://localhost:5002"
    echo "📝 Logs: tail -f redaccel_server.log"
    echo ""
    echo "To stop: pkill -f 'python3 redaccel_app.py'"
else
    echo "❌ Failed to start server. Check redaccel_server.log for errors."
    exit 1
fi

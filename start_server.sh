#!/bin/bash
# Start the Reddit Comment Tool web server

echo "Starting Reddit Comment Tool web server..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your API credentials."
    echo "See config_template.txt for reference."
    echo ""
fi

# Try to find Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "❌ Error: Python not found!"
    echo "Please install Python 3.7 or higher."
    exit 1
fi

echo "Using: $PYTHON_CMD"
echo ""

# Check if Flask is installed
if ! $PYTHON_CMD -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask not found. Installing dependencies..."
    $PYTHON_CMD -m pip install -r requirements.txt
    echo ""
fi

echo "🚀 Starting server on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

$PYTHON_CMD app.py


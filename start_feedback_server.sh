#!/bin/bash

# Product Feedback Simulator - Server Startup Script

echo "=========================================="
echo "🚀 Starting Product Feedback Simulator"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Please create a .env file with your OpenAI API key:"
    echo "   OPENAI_API_KEY=your_key_here"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check if OpenAI API key is set
if [ -f .env ]; then
    source .env
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "⚠️  Warning: OPENAI_API_KEY not found in .env file"
    else
        echo "✅ OpenAI API key found"
    fi
fi

echo ""
echo "=========================================="
echo "🌐 Starting web server..."
echo "=========================================="
echo ""
echo "📍 Server will be available at: http://localhost:5000"
echo "📝 Open this URL in your browser"
echo ""
echo "⚠️  Press Ctrl+C to stop the server"
echo ""

# Start the Flask app
python feedback_app.py

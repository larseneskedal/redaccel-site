#!/bin/bash

echo "=========================================="
echo "🚀 Starting Redaccel Marketing Website"
echo "=========================================="
echo ""
echo "📍 Server will be available at:"
echo "   http://localhost:5001"
echo ""
echo "⚠️  Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

cd "$(dirname "$0")"
python3 redaccel_app.py

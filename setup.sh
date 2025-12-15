#!/bin/bash

# Product Feedback Simulator - Automated Setup Script

echo "=========================================="
echo "🚀 Product Feedback Simulator Setup"
echo "=========================================="
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Installing pip..."
    python3 -m ensurepip --upgrade
fi

echo "✅ pip3 found"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
python3 -m pip install --upgrade pip --quiet
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Installation failed. You may need to install Xcode command line tools:"
    echo "   Run: xcode-select --install"
    exit 1
fi

echo ""
echo "✅ Dependencies installed successfully!"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    if [ -f config_template.txt ]; then
        cp config_template.txt .env
        echo "✅ .env file created"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env and add your OpenAI API key:"
        echo "   OPENAI_API_KEY=your_actual_api_key_here"
        echo ""
        echo "   Get your API key from: https://platform.openai.com/api-keys"
        echo ""
    else
        echo "⚠️  config_template.txt not found. Creating basic .env file..."
        cat > .env << EOF
# OpenAI API Key (REQUIRED)
# Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here
EOF
        echo "✅ Basic .env file created"
        echo ""
        echo "⚠️  Please edit .env and add your OpenAI API key!"
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OpenAI API key"
echo "2. Run: python3 feedback_app.py"
echo "3. Open: http://localhost:5000"
echo ""
echo "Or use the startup script:"
echo "   ./start_feedback_server.sh"
echo ""

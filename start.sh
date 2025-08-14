#!/bin/bash

echo "🚀 Starting Multi-Agent Research System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📚 Installing requirements..."
pip install -r requirements.txt

# Check for API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  Warning: GOOGLE_API_KEY environment variable not set"
    echo "Please set your Google API key:"
    echo "export GOOGLE_API_KEY='your_api_key_here'"
    echo ""
    echo "You can also create a .env file with:"
    echo "GOOGLE_API_KEY=your_api_key_here"
    echo ""
fi

echo "🧪 Running system test..."
python test_system.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🌐 Starting web server..."
    echo "Open your browser to: http://localhost:8000"
    echo "Press Ctrl+C to stop the server"
    echo ""
    python main_multiagent.py
else
    echo "❌ System test failed. Please check your configuration."
    exit 1
fi

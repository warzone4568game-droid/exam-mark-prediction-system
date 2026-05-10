#!/bin/bash
# Exam Mark Prediction System - Linux/macOS Startup Script

echo ""
echo "============================================"
echo "Exam Mark Prediction System"
echo "============================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run Flask app
echo ""
echo "Starting Flask application..."
echo "Application will be available at: http://localhost:5000"
echo ""
python3 backend/app.py

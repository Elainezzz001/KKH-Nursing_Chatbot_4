#!/bin/bash

echo "Starting KKH Nursing Chatbot..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade requirements
echo "Installing/updating dependencies..."
pip install -r requirements.txt

# Check if LM Studio is running (optional)
echo
echo "NOTE: Make sure LM Studio is running with OpenHermes model loaded"
echo "      on localhost:1234 for full functionality"
echo

# Start the application
echo "Starting Streamlit application..."
streamlit run app.py

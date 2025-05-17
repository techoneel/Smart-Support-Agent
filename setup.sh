#!/bin/bash
echo "Setting up Smart Support Agent development environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python not found. Please install Python 3.9+"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e .
pip install -e ".[test]"

# Create data directories
echo "Creating data directories..."
mkdir -p data
mkdir -p logs

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env with your API keys and configuration"
fi

echo "Setup complete! Activate the virtual environment with:"
echo "source venv/bin/activate"
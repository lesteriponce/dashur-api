#!/bin/bash

# Fix script for common Django setup issues
# Run this if you encounter "pkg_resources" or other dependency issues

echo "Fixing common Django setup issues..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Fix setuptools and pip issues
echo "Upgrading setuptools, pip, and wheel..."
pip install --upgrade pip setuptools wheel

# Reinstall requirements to ensure all dependencies are properly installed
echo "Reinstalling requirements..."
pip install -r requirements.txt --force-reinstall

# Test Django setup
echo "Testing Django setup..."
python src/dashur/manage.py check

if [ $? -eq 0 ]; then
    echo "Issues fixed successfully!"
    echo ""
    echo "You can now run:"
    echo "   source venv/bin/activate"
    echo "   python src/dashur/manage.py runserver"
else
    echo "Issues persist. Please check the error messages above."
fi

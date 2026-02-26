#!/bin/bash

# Django API Setup Script
# This script sets up a complete Django development environment

set -e  # Exit on any error

echo "Setting up Django API environment..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip, setuptools, and wheel first
echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Install requirements
echo "Installing Python requirements..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p src/dashur/logs
mkdir -p src/dashur/media
mkdir -p src/dashur/staticfiles

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please update .env file with your configuration"
fi

# Run Django migrations
echo "Running Django migrations..."
python src/dashur/manage.py migrate

# Create superuser (optional)
echo ""
echo "Do you want to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python src/dashur/manage.py createsuperuser
fi

# Collect static files
echo "Collecting static files..."
python src/dashur/manage.py collectstatic --noinput

# Run Django check
echo "Running Django system check..."
python src/dashur/manage.py check

echo ""
echo "Setup completed successfully!"
echo ""
echo "Next steps:"
echo "   1. Update .env file with your configuration"
echo "   2. Run: source venv/bin/activate"
echo "   3. Run: python src/dashur/manage.py runserver"
echo ""
echo "Your Django API will be available at: http://127.0.0.1:8000"
echo "API docs at: http://127.0.0.1:8000/api/docs/"
echo "Admin panel at: http://127.0.0.1:8000/admin/"

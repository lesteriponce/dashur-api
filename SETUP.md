# Dashur API Setup Instructions

## Quick Setup

### Option 1: Automated Setup (Recommended)
```bash
# Clone or download the project
cd dashur-api

# Run the setup script
./setup.sh
```

### Option 2: Manual Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade essential packages first
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run migrations
python src/dashur/manage.py migrate

# Create superuser (optional)
python src/dashur/manage.py createsuperuser

# Collect static files
python src/dashur/manage.py collectstatic --noinput

# Run the development server
python src/dashur/manage.py runserver
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- git (for cloning)

## Common Issues and Solutions

### 1. "Command 'python' not found"
**Problem**: Your system uses `python3` instead of `python`

**Solution**: Always use `python3` instead of `python`:
```bash
python3 -m venv venv
source venv/bin/activate
python src/dashur/manage.py runserver
```

### 2. "ModuleNotFoundError: No module named 'pkg_resources'"
**Problem**: Missing setuptools package

**Solution**: Upgrade setuptools:
```bash
source venv/bin/activate
pip install --upgrade setuptools wheel
```

### 3. "No such file or directory: 'logs/django.log'"
**Problem**: Logs directory doesn't exist

**Solution**: This is now automatically handled, but if you encounter this:
```bash
mkdir -p src/dashur/logs
```

### 4. Virtual environment issues
**Problem**: Dependencies not found after activation

**Solution**: Recreate the virtual environment:
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Environment Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update the `.env` file with your settings:
- `SECRET_KEY`: Generate a secure key
- `DEBUG`: Set to `False` in production
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

## Running the Application

### Development Server
```bash
source venv/bin/activate
python src/dashur/manage.py runserver
```

### Production Server
```bash
source venv/bin/activate
gunicorn src.dashur.dashur.wsgi:application --bind 0.0.0.0:8000
```

## Available URLs

- **API**: http://127.0.0.1:8000/api/
- **API Documentation**: http://127.0.0.1:8000/api/docs/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Wagtail CMS**: http://127.0.0.1:8000/admin/

## Project Structure

```
dashur-api/
├── src/dashur/          # Main Django project
│   ├── dashur/          # Project settings
│   ├── authentication/  # User authentication
│   ├── careers/         # Careers app
│   ├── contacts/        # Contacts app
│   └── logs/            # Log files (auto-created)
├── venv/                # Virtual environment
├── requirements.txt     # Python dependencies
├── .env.example        # Environment template
└── setup.sh            # Automated setup script
```

## Development Workflow

1. Make sure virtual environment is activated:
```bash
source venv/bin/activate
```

2. Create migrations after model changes:
```bash
python src/dashur/manage.py makemigrations
python src/dashur/manage.py migrate
```

3. Run tests:
```bash
python src/dashur/manage.py test
```

4. Collect static files after changes:
```bash
python src/dashur/manage.py collectstatic --noinput
```

## Deployment Notes

- Set `DEBUG=False` in production
- Use environment variables for sensitive data
- Configure proper database (PostgreSQL recommended)
- Set up Redis for Celery
- Configure static file serving
- Set up proper logging

## Support

If you encounter any issues:

1. Check that you're using Python 3.8+
2. Ensure virtual environment is activated
3. Verify all dependencies are installed
4. Check the error logs in `src/dashur/logs/django.log`

## License

[Add your license information here]

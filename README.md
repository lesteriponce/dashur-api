# Dashur API

A comprehensive Django REST API with Wagtail CMS integration for the Dashur AI frontend.

## Overview

This project provides a robust backend API with modern authentication, content management, and business logic for the Dashur AI platform. It follows Django best practices and is designed for scalability and maintainability.

## Features

- **Authentication**: JWT-based authentication with user registration, login, and profile management
- **Careers**: Job position management and application tracking system
- **Contacts**: Contact form submission and response management
- **Admin Interface**: Wagtail CMS integration for content management
- **Security**: CORS configuration, rate limiting, file upload validation
- **Documentation**: Auto-generated API documentation with Swagger/OpenAPI
- **Logging**: Comprehensive logging system with automatic directory creation
- **Error Handling**: Standardized API response format with proper error handling

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework 3.14
- **CMS**: Wagtail 5.2
- **Authentication**: JWT with SimpleJWT
- **Database**: SQLite (development), PostgreSQL (production)
- **File Storage**: Local storage (configurable for cloud storage)
- **Documentation**: drf-spectacular (Swagger/OpenAPI)
- **Task Queue**: Celery with Redis (optional)
- **Logging**: Python logging with rotating file handlers

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (for production)
- Redis (optional, for caching and Celery tasks)

### Option 1: Automated Setup (Recommended)

```bash
# Clone or download the project
git clone <repository-url>
cd dashur-api

# Run the setup script
./setup.sh
```

### Option 2: Manual Setup

1. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install essential packages first**
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python src/dashur/manage.py makemigrations
   python src/dashur/manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python src/dashur/manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python src/dashur/manage.py collectstatic --noinput
   ```

8. **Run development server**
   ```bash
   python src/dashur/manage.py runserver
   ```

### Common Setup Issues

If you encounter dependency issues, run the fix script:

```bash
./fix.sh
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/update/` - Update user profile
- `POST /api/auth/password/change/` - Change password
- `GET /api/auth/me/` - Get current user info

### Careers
- `GET /api/careers/positions/` - List job positions
- `POST /api/careers/positions/` - Create job position (admin only)
- `GET /api/careers/positions/{id}/` - Get job position details
- `PUT /api/careers/positions/{id}/` - Update job position (admin only)
- `DELETE /api/careers/positions/{id}/` - Delete job position (admin only)
- `GET /api/careers/applications/my/` - Get current user's applications
- `GET /api/careers/stats/` - Application statistics (admin only)
- `GET /api/careers/dashboard/stats/` - Dashboard statistics (admin only)
- `GET /api/careers/dashboard/activity/` - Recent activity (admin only)

### Contacts
- `GET /api/contacts/` - List contact submissions
- `POST /api/contacts/` - Submit contact form
- `GET /api/contacts/{id}/` - Get contact submission details
- `PUT /api/contacts/{id}/` - Update contact submission (admin only)
- `GET /api/contacts/responses/` - List contact responses
- `POST /api/contacts/responses/` - Create contact response (admin only)
- `GET /api/contacts/stats/` - Contact statistics (admin only)

### Admin Interface (Session Authentication)
- `POST /api/admin/careers/applications/` - Submit job application (file upload support)
- `GET /api/admin/careers/applications/` - List job applications
- `GET /api/admin/careers/applications/{id}/` - Get application details
- `PUT /api/admin/careers/applications/{id}/` - Update application (admin only)

### Documentation
- `GET /api/docs/` - Swagger UI documentation
- `GET /api/redoc/` - ReDoc documentation
- `GET /api/schema/` - OpenAPI schema

## Project Structure

```
dashur-api/
├── src/dashur/              # Main Django project
│   ├── dashur/              # Project settings and configuration
│   │   ├── settings/        # Environment-specific settings
│   │   │   ├── base.py      # Base settings (logging, apps, etc.)
│   │   │   ├── development.py # Development-specific settings
│   │   │   └── production.py  # Production-specific settings
│   │   ├── urls.py          # Main URL configuration
│   │   ├── utils.py         # Utility functions
│   │   ├── middleware.py    # Custom middleware
│   │   └── wsgi.py          # WSGI configuration
│   ├── authentication/     # User authentication app
│   │   ├── models.py        # Custom User model and preferences
│   │   ├── views.py         # Authentication views
│   │   ├── serializers.py   # API serializers
│   │   └── urls.py          # App URLs
│   ├── careers/            # Job management app
│   │   ├── models.py        # JobPosition and JobApplication models
│   │   ├── views.py         # Career-related views
│   │   ├── serializers.py   # API serializers
│   │   ├── urls.py          # JWT API URLs
│   │   └── admin_urls.py    # Admin API URLs (Session auth)
│   ├── contacts/           # Contact management app
│   │   ├── models.py        # Contact and response models
│   │   ├── views.py         # Contact-related views
│   │   ├── serializers.py   # API serializers
│   │   └── urls.py          # App URLs
│   ├── logs/               # Log files (auto-created)
│   ├── media/              # User uploaded files
│   ├── static/             # Static files
│   └── manage.py           # Django management script
├── venv/                   # Virtual environment
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── setup.sh               # Automated setup script
├── fix.sh                 # Common issues fix script
├── SETUP.md               # Detailed setup instructions
└── README.md              # This file
```

## Development Workflow

### Environment Setup

1. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   ```

2. **Check Django system**
   ```bash
   python src/dashur/manage.py check
   ```

3. **Run development server**
   ```bash
   python src/dashur/manage.py runserver
   ```

### Making Changes

1. **Model changes**
   ```bash
   python src/dashur/manage.py makemigrations
   python src/dashur/manage.py migrate
   ```

2. **Static file changes**
   ```bash
   python src/dashur/manage.py collectstatic --noinput
   ```

3. **Testing**
   ```bash
   python src/dashur/manage.py test
   ```

### Code Quality

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Write tests for new functionality
- Keep commits small and focused

## Data Models

### Authentication

**User Model** (Custom AbstractUser)
- `email`: Email field (unique identifier)
- `first_name`, `last_name`: User names
- `phone`: Optional phone number
- `is_active`, `is_staff`, `is_superuser`: Standard Django fields
- Custom manager using email as username

**UserPreference Model**
- `user`: One-to-one relationship with User
- `theme`: UI theme preference
- `language`: Language preference
- `notifications`: Notification settings

### Careers

**JobPosition Model**
- `title`: Job title
- `department`: Department name
- `employment_type`: full_time, part_time, contract, internship, freelance
- `status`: active, inactive, draft, closed
- `description`, `requirements`, `responsibilities`, `benefits`: Text fields
- `salary_min`, `salary_max`: Salary range
- `location`: Job location
- `is_remote`: Remote work option
- `application_deadline`: Application deadline
- `created_at`, `updated_at`: Timestamps

**JobApplication Model**
- `position`: Foreign key to JobPosition
- `applicant`: Foreign key to User
- `full_name`, `email`, `phone`: Applicant information
- `cover_letter`: Application cover letter
- `resume`: Resume file upload
- `status`: pending, reviewing, accepted, rejected
- `applied_at`: Application timestamp

### Contacts

**ContactSubmission Model**
- `name`: Contact name
- `email`: Contact email
- `phone`: Optional phone number
- `subject`: Message subject
- `message`: Message content
- `status`: pending, responded, closed
- `created_at`: Submission timestamp

**ContactResponse Model**
- `submission`: Foreign key to ContactSubmission
- `responder`: Foreign key to User (admin)
- `response`: Response message
- `responded_at`: Response timestamp

## Testing

### Run Tests

```bash
# Run all tests
python src/dashur/manage.py test

# Run specific app tests
python src/dashur/manage.py test authentication
python src/dashur/manage.py test careers
python src/dashur/manage.py test contacts
```

### Test Coverage

```bash
coverage run --source='.' src/dashur/manage.py test
coverage report
coverage html  # Generate HTML report
```

## Environment Configuration

### Required Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Core Django settings
SECRET_KEY=your-secret-key-here
DJANGO_ENVIRONMENT=development
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for production)
DB_NAME=dashur_db
DB_USER=dashur_user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Deployment

### Production Setup

1. **Environment Preparation**
   ```bash
   export DJANGO_ENVIRONMENT=production
   export DEBUG=False
   ```

2. **Database Setup**
   - Configure PostgreSQL database
   - Update environment variables
   - Run migrations: `python src/dashur/manage.py migrate`

3. **Static Files**
   ```bash
   python src/dashur/manage.py collectstatic --noinput
   ```

4. **Web Server Configuration**
   - Configure Nginx/Apache
   - Set up SSL certificates
   - Configure reverse proxy

5. **Application Server**
   ```bash
   gunicorn src.dashur.dashur.wsgi:application --bind 0.0.0.0:8000
   ```

### Security Considerations

- Set `DEBUG=False` in production
- Use strong `SECRET_KEY`
- Configure proper database credentials
- Set up CORS for your frontend domain
- Use HTTPS in production
- Regular security updates

## API Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "data": {},
  "message": "Operation successful",
  "errors": null
}
```

Error responses:
```json
{
  "success": false,
  "data": null,
  "message": "Error occurred",
  "errors": {
    "field": ["Error message"]
  }
}
```

## Authentication

### JWT Authentication

The API uses JWT tokens for authentication:

1. **Login**: Get access and refresh tokens
2. **Access Token**: Valid for 60 minutes
3. **Refresh Token**: Valid for 7 days
4. **Token Refresh**: Use refresh token to get new access token

### Authorization Headers

Include JWT token in API requests:

```bash
Authorization: Bearer <access_token>
```

## Logging

The application includes comprehensive logging:

- **Console logging**: Always available
- **File logging**: Automatically created in `src/dashur/logs/django.log`
- **Log rotation**: 5MB max file size, 5 backup files
- **Log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Log Levels Usage

- **DEBUG**: Detailed development information
- **INFO**: General application flow
- **WARNING**: Potentially harmful situations
- **ERROR**: Error events that might allow continuation
- **CRITICAL**: Severe errors that may stop the application

## Security Features

- JWT authentication with refresh tokens
- CORS configuration for frontend integration
- File upload validation and security
- Rate limiting to prevent abuse
- Security headers (XSS protection, content type options)
- Input validation and sanitization
- Environment variable protection
- Secure password hashing

## Troubleshooting

### Common Issues

1. **"Command 'python' not found"**
   - Use `python3` instead of `python`

2. **"ModuleNotFoundError: No module named 'pkg_resources'"**
   - Run `./fix.sh` or manually upgrade setuptools

3. **"No such file or directory: 'logs/django.log'"**
   - This is automatically handled, but if it persists:
   ```bash
   mkdir -p src/dashur/logs
   ```

4. **Virtual environment issues**
   ```bash
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

### Getting Help

1. Check the error logs in `src/dashur/logs/django.log`
2. Run `python src/dashur/manage.py check` for system validation
3. Ensure all environment variables are set correctly
4. Verify database connection and permissions

## Contributing

### For New Team Members

1. **Setup your environment**
   ```bash
   git clone <repository-url>
   cd dashur-api
   ./setup.sh
   ```

2. **Understand the codebase**
   - Read this README thoroughly
   - Review the project structure
   - Examine existing models and views
   - Check API documentation at `/api/docs/`

3. **Development workflow**
   - Create feature branches from main
   - Write tests for new functionality
   - Follow coding standards
   - Document your changes

4. **Code review process**
   - Submit pull requests
   - Address review feedback
   - Ensure tests pass
   - Update documentation

### Guidelines

- Follow Django and Python best practices
- Write clear, maintainable code
- Add appropriate tests
- Update documentation
- Keep security in mind
- Use meaningful commit messages

### Development Standards

1. **Code Style**
   - Follow PEP 8
   - Use descriptive variable names
   - Add docstrings to functions and classes
   - Keep functions focused and small

2. **Testing**
   - Write unit tests for new features
   - Test edge cases and error conditions
   - Maintain test coverage above 80%
   - Use descriptive test names

3. **Documentation**
   - Update README for major changes
   - Document API endpoints
   - Add inline comments for complex logic
   - Keep changelog updated

## Available URLs

### Development Server
- **API Base**: http://127.0.0.1:8000/api/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Documentation**: http://127.0.0.1:8000/api/docs/
- **ReDoc Documentation**: http://127.0.0.1:8000/api/redoc/

### Key Endpoints
- **Authentication**: `/api/auth/`
- **Careers**: `/api/careers/`
- **Contacts**: `/api/contacts/`
- **Admin**: `/api/admin/careers/` (file upload support)

## License

This project is licensed under the MIT License.

## Support

For questions or issues:

1. Check this README first
2. Review the SETUP.md file for detailed instructions
3. Check the error logs in `src/dashur/logs/django.log`
4. Run `python src/dashur/manage.py check` for system validation
5. Contact the development team

---

**Last Updated**: February 2026
**Version**: 1.0.0
**Django Version**: 4.2.7
**Python Requirements**: 3.8+

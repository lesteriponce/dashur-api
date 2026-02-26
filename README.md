# Dashur API

A comprehensive Django REST API with Wagtail CMS integration for the Dashur AI frontend.

## Features

- **Authentication**: JWT-based authentication with user registration, login, and profile management
- **Careers**: Job position management and application tracking system
- **Contacts**: Contact form submission and response management
- **Admin Interface**: Wagtail CMS integration for content management
- **Security**: CORS configuration, rate limiting, file upload validation
- **Documentation**: Auto-generated API documentation with Swagger/OpenAPI

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework 3.14
- **CMS**: Wagtail 5.2
- **Authentication**: JWT with SimpleJWT
- **Database**: SQLite (development), PostgreSQL (production)
- **File Storage**: Local storage (configurable for cloud storage)
- **Documentation**: drf-spectacular (Swagger/OpenAPI)
- **Task Queue**: Celery with Redis (optional)

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (for production)
- Redis (optional, for caching and Celery tasks)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dashur-api
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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
   python src/dashur/manage.py collectstatic
   ```

8. **Run development server**
   ```bash
   python src/dashur/manage.py runserver
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
- `GET /api/careers/applications/` - List job applications
- `POST /api/careers/applications/` - Submit job application
- `GET /api/careers/applications/{id}/` - Get application details
- `PUT /api/careers/applications/{id}/` - Update application (admin only)
- `GET /api/careers/applications/my/` - Get current user's applications
- `GET /api/careers/stats/` - Application statistics (admin only)

### Contacts
- `GET /api/contacts/` - List contact submissions
- `POST /api/contacts/` - Submit contact form
- `GET /api/contacts/{id}/` - Get contact submission details
- `PUT /api/contacts/{id}/` - Update contact submission (admin only)
- `GET /api/contacts/responses/` - List contact responses
- `POST /api/contacts/responses/` - Create contact response (admin only)
- `GET /api/contacts/stats/` - Contact statistics (admin only)

### Documentation
- `GET /api/docs/` - Swagger UI documentation
- `GET /api/redoc/` - ReDoc documentation
- `GET /api/schema/` - OpenAPI schema

## Admin Interface

Access the Wagtail admin interface at `/admin/` with your superuser credentials.

## Project Structure

```
dashur-api/
├── src/dashur/
│   ├── dashur/
│   │   ├── settings/
│   │   │   ├── base.py          # Base settings
│   │   │   ├── development.py   # Development settings
│   │   │   └── production.py    # Production settings
│   │   ├── urls.py              # Main URL configuration
│   │   ├── utils.py             # Utility functions
│   │   ├── middleware.py        # Custom middleware
│   │   ├── validators.py        # Custom validators
│   │   ├── permissions.py       # Custom permissions
│   │   └── wagtail_hooks.py     # Wagtail customization
│   ├── authentication/          # Authentication app
│   ├── careers/                # Careers app
│   ├── contacts/               # Contacts app
│   └── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## Testing

Run tests with:
```bash
python src/dashur/manage.py test
```

Run tests with coverage:
```bash
coverage run --source='.' src/dashur/manage.py test
coverage report
coverage html
```

## Deployment

### Environment Variables

Key environment variables for production:

- `SECRET_KEY`: Django secret key
- `DJANGO_ENVIRONMENT`: Set to 'production'
- `DEBUG`: Set to False
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DB_*`: Database configuration
- `REDIS_URL`: Redis connection URL
- `EMAIL_*`: Email configuration
- `CORS_ALLOWED_ORIGINS`: Allowed frontend origins

### Production Setup

1. **Set environment variables**
2. **Install production dependencies**
3. **Run database migrations**
4. **Collect static files**
5. **Configure web server (Nginx/Apache)**
6. **Set up application server (Gunicorn)**
7. **Configure SSL certificates**

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

## Security Features

- JWT authentication with refresh tokens
- CORS configuration for frontend integration
- File upload validation and security
- Rate limiting to prevent abuse
- Security headers (XSS protection, content type options)
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and ensure they pass
6. Submit a pull request

## License

This project is licensed under the MIT License.

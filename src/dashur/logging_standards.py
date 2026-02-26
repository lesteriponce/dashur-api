"""
Logging standards for Dashur API.
Defines consistent logging levels and patterns.
"""

# LOGGING LEVELS USAGE GUIDE:
#
# DEBUG: Detailed information for debugging purposes
# - Request/response payloads in development
# - Database query details
# - Authentication flow details
# - File processing steps
#
# INFO: General information about application flow
# - User actions (login, registration, CRUD operations)
# - Successful operations
# - Business process milestones
# - System startup/shutdown events
#
# WARNING: Potentially harmful situations
# - Rate limiting
# - Failed authentication attempts
# - Deprecated API usage
# - Resource usage warnings
# - Configuration issues
#
# ERROR: Error events that might still allow the application to continue
# - Failed operations (database, email, external API calls)
# - Exception handling
# - Validation failures
# - Missing required resources
#
# CRITICAL: Very severe error events that might cause the application to stop
# - System crashes
# - Database connection failures
# - Security breaches
# - Out of memory errors

# Standardized log message formats
LOG_FORMATS = {
    'user_action': "User {action}: {user_email} - {details}",
    'api_request': "API {method} {path} - IP: {ip} - User: {user} - Status: {status}",
    'error_operation': "Error in {operation}: {error}",
    'warning_rate_limit': "Rate limit exceeded for IP: {ip} - Requests: {count}",
    'success_operation': "{operation} successful: {details}",
    'security_event': "Security event: {event_type} - {details}",
}

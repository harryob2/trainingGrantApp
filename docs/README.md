# Flask Survey Form System Documentation

## Overview

The Flask Survey Form System is a comprehensive web application designed for managing training form submissions within an organization. Built with Flask (Python) and modern frontend technologies, it provides a complete workflow for training management from submission to approval and export.

## System Architecture

### Technology Stack
- **Backend**: Flask (Python web framework)
- **Database**: SQLite (development) / MariaDB (production)
- **Authentication**: LDAP integration with Flask-Login
- **Frontend**: HTML5, CSS3, JavaScript with Bootstrap
- **Testing**: Playwright for end-to-end testing
- **Package Management**: uv (Python), npm (Node.js)

### Core Components

1. **Web Application** (`app.py`) - Main Flask application with routes and business logic
2. **Database Models** (`models.py`) - SQLAlchemy ORM models and database operations
3. **Forms** (`forms.py`) - WTForms for form validation and rendering
4. **Authentication** (`auth.py`) - LDAP authentication and user management
5. **Configuration** (`config.py`) - Application settings and environment variables
6. **Utilities** (`utils.py`) - Helper functions for file handling and data processing
7. **Lookups** (`lookups.py`) - Data lookup services for employees and training catalog

## Key Features

### User Management
- **LDAP Authentication**: Secure login using corporate LDAP directory
- **Role-Based Access**: Admin and regular user roles with different permissions
- **Session Management**: Secure session handling with Flask-Login

### Training Form Management
- **Form Submission**: Comprehensive training form with validation
- **File Attachments**: Support for multiple file types with secure upload
- **Dynamic Validation**: Context-aware form validation based on training type
- **Edit Capability**: Users can edit their own submissions before approval

### Administrative Features
- **Approval Workflow**: Admin approval system for training submissions
- **User Administration**: Manage admin users through web interface
- **Search and Filter**: Advanced search capabilities with multiple criteria
- **Export Functionality**: Export approved forms to Claim 5 format

### Data Management
- **Employee Lookup**: Integration with employee directory
- **Training Catalog**: Predefined training courses with autocomplete
- **Cost Tracking**: Comprehensive expense tracking for training activities
- **Audit Trail**: Complete submission and approval history

## Data Flow

### 1. User Authentication Flow
```
User Login → LDAP Verification → Session Creation → Role Assignment → Dashboard Access
```

### 2. Form Submission Flow
```
Form Creation → Validation → File Upload → Database Storage → Confirmation → Admin Notification
```

### 3. Approval Flow
```
Admin Review → Approval Decision → Status Update → User Notification → Export Eligibility
```

### 4. Export Flow
```
Filter Approved Forms → Generate Excel → Apply Formatting → Download/Save
```

## Database Schema

### Core Tables
- **training_forms**: Main training submission data
- **attachments**: File attachments linked to forms
- **admins**: Administrative users
- **training_catalog**: Predefined training courses

### Relationships
- One-to-Many: TrainingForm → Attachments
- Many-to-Many: Users ↔ Roles (through LDAP groups)

## Security Features

### Authentication & Authorization
- LDAP integration for corporate authentication
- Role-based access control (Admin/User)
- Session management with secure cookies
- CSRF protection on all forms

### File Security
- Secure filename handling
- File type validation
- Upload size limits
- Isolated file storage

### Data Protection
- SQL injection prevention through ORM
- XSS protection through template escaping
- Input validation and sanitization

## Deployment Architecture

### Development Environment
- SQLite database for local development
- Debug mode enabled
- Local file storage
- Test LDAP bypass accounts

### Production Environment
- MariaDB database on dedicated server
- Network file storage for attachments
- LDAP authentication against corporate directory
- SSL/TLS encryption

## File Structure

```
FlaskSurveyForm/
├── docs/                    # Documentation files
├── static/                  # Static web assets
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   ├── images/             # Image assets
│   └── data/               # Static data files
├── templates/              # Jinja2 HTML templates
├── tests/                  # Test files
│   └── e2e/               # End-to-end tests
├── uploads/               # File upload storage
├── migrations/            # Database migration scripts
├── app.py                 # Main Flask application
├── models.py              # Database models
├── forms.py               # Form definitions
├── auth.py                # Authentication logic
├── config.py              # Configuration settings
├── utils.py               # Utility functions
├── lookups.py             # Data lookup services
├── setup_db.py            # Database initialization
└── main.py                # Application entry point
```

## Related Documentation

- [Application Architecture](./architecture.md) - Detailed system architecture
- [Database Schema](./database.md) - Complete database documentation
- [API Reference](./api.md) - API endpoints and usage
- [Authentication System](./authentication.md) - Authentication and authorization
- [Form System](./forms.md) - Form validation and processing
- [File Management](./file-management.md) - File upload and storage
- [Testing Guide](./testing.md) - Testing procedures and guidelines
- [Deployment Guide](./deployment.md) - Deployment and configuration
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

## Getting Started

1. **Setup**: Follow the setup instructions in the main README.md
2. **Configuration**: Review and update `config.py` for your environment
3. **Database**: Run `python setup_db.py` to initialize the database
4. **Testing**: Run the test suite to verify functionality
5. **Deployment**: Follow the deployment guide for production setup

## Support and Maintenance

For technical support, bug reports, or feature requests, please contact the development team or create an issue in the project repository. 
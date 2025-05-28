# Application Architecture

## System Overview

The Flask Survey Form System follows a traditional Model-View-Controller (MVC) architecture pattern, implemented using Flask's blueprint-style organization. The application is designed as a monolithic web application with clear separation of concerns.

## Architecture Layers

### 1. Presentation Layer (Templates & Static Files)

**Location**: `templates/`, `static/`

**Purpose**: Handles user interface and user experience

**Components**:
- **HTML Templates** (`templates/`): Jinja2 templates for dynamic content rendering
- **CSS Stylesheets** (`static/css/`): Bootstrap-based responsive styling
- **JavaScript** (`static/js/`): Client-side interactivity and AJAX calls
- **Images & Assets** (`static/images/`, `static/data/`): Static resources

**Key Templates**:
- `base.html`: Master template with common layout and navigation
- `index.html`: Main form submission interface
- `list.html`: Training submissions listing with search/filter
- `view.html`: Individual form viewing interface
- `login.html`: Authentication interface

### 2. Application Layer (Flask Routes & Controllers)

**Location**: `app.py`

**Purpose**: Handles HTTP requests, business logic orchestration, and response generation

**Key Route Groups**:

#### Authentication Routes
- `/login` - User authentication via LDAP
- `/logout` - Session termination
- `/manage_admins` - Admin user management

#### Form Management Routes
- `/` - Home dashboard
- `/submit` - Form submission (GET/POST)
- `/edit/<id>` - Form editing
- `/view/<id>` - Form viewing
- `/approve/<id>` - Admin approval action

#### Data Management Routes
- `/list` - Form listing with search/filter
- `/my_submissions` - User's own submissions
- `/leaderboard` - Training statistics dashboard

#### API Routes
- `/api/employees` - Employee lookup service
- `/api/lookup/<type>` - Generic lookup service
- `/api/export_claim5_options` - Export configuration

#### File Management Routes
- `/uploads/<filename>` - Secure file serving
- `/export_claim5` - Excel export generation

### 3. Business Logic Layer (Services & Utilities)

**Location**: `utils.py`, `lookups.py`, `forms.py`

**Purpose**: Implements business rules, data processing, and validation logic

#### Form Processing (`forms.py`)
- **TrainingForm**: Main form with dynamic validation
- **SearchForm**: Search and filtering interface
- **LoginForm**: Authentication form
- **InvoiceForm**: Invoice attachment handling

#### Data Services (`lookups.py`)
- **Employee Lookup**: CSV-based employee directory integration
- **Training Catalog**: Database-driven training course lookup
- **Caching**: In-memory caching for performance optimization

#### Utilities (`utils.py`)
- **File Handling**: Secure file upload and storage
- **Data Preparation**: Form data processing for database storage
- **Validation**: File type and size validation

### 4. Data Access Layer (Models & Database)

**Location**: `models.py`, `setup_db.py`

**Purpose**: Handles data persistence, database operations, and ORM mapping

#### Database Models
- **TrainingForm**: Core training submission entity
- **Attachment**: File attachment metadata
- **Admin**: Administrative user records
- **TrainingCatalog**: Predefined training courses

#### Database Operations
- **CRUD Operations**: Create, Read, Update, Delete for all entities
- **Search & Filter**: Complex querying with multiple criteria
- **Pagination**: Efficient data retrieval for large datasets
- **Transactions**: Atomic operations with rollback capability

### 5. Authentication & Security Layer

**Location**: `auth.py`

**Purpose**: Handles user authentication, authorization, and security

#### Authentication Components
- **LDAP Integration**: Corporate directory authentication
- **Flask-Login**: Session management and user state
- **User Model**: User representation and role management
- **Bypass Authentication**: Development/testing user accounts

#### Security Features
- **Role-Based Access Control**: Admin vs. regular user permissions
- **Session Security**: Secure cookie configuration
- **CSRF Protection**: Cross-site request forgery prevention
- **Input Validation**: XSS and injection attack prevention

## Data Flow Architecture

### 1. Request Processing Flow

```
HTTP Request → Flask Router → Route Handler → Business Logic → Data Layer → Database
                     ↓
Response ← Template Rendering ← Data Processing ← Query Results ← Database Response
```

### 2. Authentication Flow

```
Login Request → LDAP Server → User Verification → Session Creation → Role Assignment
                     ↓
Access Control ← Permission Check ← User Session ← Flask-Login ← Session Store
```

### 3. Form Submission Flow

```
Form Data → Validation → File Upload → Data Processing → Database Storage
     ↓
Confirmation ← Template Render ← Success Response ← Transaction Commit
```

## Component Interactions

### Core Dependencies

```
app.py (Main Application)
├── models.py (Database Layer)
├── forms.py (Form Validation)
├── auth.py (Authentication)
├── utils.py (Utilities)
├── lookups.py (Data Services)
└── config.py (Configuration)
```

### External Dependencies

```
Flask Framework
├── SQLAlchemy (ORM)
├── Flask-Login (Session Management)
├── Flask-WTF (Form Handling)
├── Werkzeug (WSGI Utilities)
└── Jinja2 (Template Engine)

LDAP Integration
├── ldap3 (LDAP Client)
└── Corporate LDAP Server

File System
├── Local Storage (Development)
└── Network Storage (Production)
```

## Design Patterns

### 1. Model-View-Controller (MVC)
- **Models**: Database entities and business logic (`models.py`)
- **Views**: HTML templates and presentation logic (`templates/`)
- **Controllers**: Route handlers and request processing (`app.py`)

### 2. Repository Pattern
- Database operations abstracted through model functions
- Consistent interface for data access across the application
- Transaction management and error handling centralized

### 3. Factory Pattern
- Flask application factory for configuration management
- Database session factory for connection management
- Form factory for dynamic form generation

### 4. Decorator Pattern
- Authentication decorators for route protection
- Validation decorators for form processing
- Error handling decorators for consistent error responses

## Scalability Considerations

### Current Architecture Limitations
- **Monolithic Design**: Single application instance
- **SQLite Database**: File-based database for development
- **Local File Storage**: Limited to single server
- **Session Storage**: In-memory session management

### Production Scalability Features
- **MariaDB Database**: Dedicated database server
- **Network File Storage**: Centralized file management
- **LDAP Integration**: Centralized authentication
- **Stateless Design**: Session data stored externally

### Future Scalability Options
- **Microservices**: Split into smaller, focused services
- **Load Balancing**: Multiple application instances
- **Caching Layer**: Redis or Memcached for performance
- **CDN Integration**: Static asset delivery optimization
- **Database Clustering**: High availability database setup

## Security Architecture

### Authentication Security
- **LDAP Integration**: Corporate directory authentication
- **Session Management**: Secure session handling
- **Password Security**: No local password storage
- **Multi-Factor Authentication**: Ready for MFA integration

### Authorization Security
- **Role-Based Access**: Admin and user role separation
- **Resource Protection**: Route-level access control
- **Data Isolation**: User can only access own data
- **Admin Privileges**: Elevated access for administrative functions

### Data Security
- **Input Validation**: Comprehensive form validation
- **SQL Injection Prevention**: ORM-based database access
- **XSS Protection**: Template-based output escaping
- **File Upload Security**: Type and size validation

### Network Security
- **HTTPS Support**: SSL/TLS encryption ready
- **CSRF Protection**: Cross-site request forgery prevention
- **Secure Headers**: Security header configuration
- **Network Isolation**: Database and file server separation

## Performance Architecture

### Current Performance Features
- **Database Indexing**: Optimized query performance
- **Pagination**: Efficient large dataset handling
- **Caching**: In-memory lookup data caching
- **Static Asset Optimization**: Minified CSS/JS

### Performance Monitoring
- **Logging**: Comprehensive application logging
- **Error Tracking**: Exception monitoring and reporting
- **Database Monitoring**: Query performance tracking
- **File Upload Monitoring**: Upload size and type tracking

### Optimization Opportunities
- **Database Query Optimization**: Query analysis and tuning
- **Caching Strategy**: Redis-based caching implementation
- **Asset Optimization**: CDN and compression
- **Background Processing**: Async task processing for exports 
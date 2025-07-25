# Application Architecture

## System Overview

The Flask Survey Form System follows a traditional Model-View-Controller (MVC) architecture pattern, implemented using Flask's blueprint-style organization. The application is designed as a monolithic web application with clear separation of concerns and enhanced user experience through progressive form disclosure.

## Architecture Layers

### 1. Presentation Layer (Templates & Static Files)

**Location**: `templates/`, `static/`

**Purpose**: Handles user interface and user experience

**Components**:
- **HTML Templates** (`templates/`): Jinja2 templates for dynamic content rendering with enhanced UI components
- **CSS Stylesheets** (`static/css/`): Bootstrap-based responsive styling with modular custom components and approve button system
- **JavaScript** (`static/js/`): Modular client-side functionality including profile picture management, form interactions, and AJAX calls
- **Images & Assets** (`static/images/`, `static/data/`): Static resources

**Key Templates**:
- `base.html`: Master template with common layout and navigation
- `home.html`: Application home/dashboard interface
- `index.html`: Multi-section training form submission interface
- `list.html`: Training submissions listing with advanced search/filter
- `view.html`: Comprehensive form viewing interface with all related data
- `login.html`: Authentication interface
- `leaderboard.html`: Training statistics and analytics dashboard

### 2. Application Layer (Flask Routes & Controllers)

**Location**: `app.py`

**Purpose**: Handles HTTP requests, business logic orchestration, and response generation

**Key Route Groups**:

#### Authentication Routes
- `/login` - User authentication via LDAP
- `/logout` - Session termination
- `/manage_admins` - Admin user management

#### Navigation Routes
- `/` - Home dashboard
- `/new` - New training form submission interface
- `/leaderboard` - Training statistics and analytics

#### Form Management Routes
- `/submit` - Form submission processing (POST)
- `/edit/<id>` - Form editing
- `/view/<id>` - Form viewing with complete details
- `/approve/<id>` - Admin approval action
- `/delete/<id>` - **NEW**: Soft delete form submission (admin or submitter only)
- `/recover/<id>` - **NEW**: Recover soft-deleted form submission (admin or submitter only)
- `/success` - Submission confirmation

#### Data Management Routes
- `/list` - Form listing with advanced search/filter
- `/my_submissions` - User's own submissions

#### API Routes
- `/api/employees` - Employee lookup service
- `/api/lookup/<type>` - Generic lookup service (trainings, employees)
- `/api/export_claim5_options` - Export configuration

#### File Management Routes
- `/uploads/<filename>` - Secure file serving
- `/export_claim5` - Enhanced Excel export generation

### 3. Business Logic Layer (Services & Utilities)

**Location**: `utils.py`, `lookups.py`, `forms.py`

**Purpose**: Implements business rules, data processing, and validation logic

#### Form Processing (`forms.py`)
- **TrainingForm**: Main form with progressive disclosure and enhanced validation
- **SearchForm**: Advanced search and filtering interface
- **LoginForm**: Authentication form
- **InvoiceForm**: Invoice attachment handling

**Enhanced Features**:
- Progressive form disclosure
- Training catalog integration
- Multi-section layout (Training Details, Trainees, Travel Expenses, Material Expenses, Attachments)
- Dynamic validation based on training type and location

#### Data Services (`lookups.py`)
- **Employee Lookup**: Database-driven employee directory integration with automated synchronization and CSV fallback
- **Training Catalog**: Database-driven training course lookup with search capabilities
- **Caching**: In-memory caching for performance optimization

#### Utilities (`utils.py`)
- **File Handling**: Secure file upload and storage with form-specific organization
- **Data Preparation**: Enhanced form data processing for complex database storage
- **Validation**: File type, size, and business rule validation

### 4. Data Access Layer (Models & Database)

**Location**: `models.py`, `setup_db.py`

**Purpose**: Handles data persistence, database operations, and ORM mapping

#### Database Models
- **TrainingForm**: Core training submission entity with comprehensive fields
- **Trainee**: Individual trainee records with department tracking
- **TravelExpense**: Travel expense tracking for training-related travel
- **MaterialExpense**: Material cost tracking for training delivery
- **Attachment**: File attachment metadata
- **Admin**: Administrative user records
- **TrainingCatalog**: Predefined training courses
- **Employee**: Employee directory with automated synchronization

**Enhanced Features**:
- Comprehensive relationship mapping
- Cascade deletion for data integrity
- Enhanced search and filtering capabilities
- Support for complex data structures

#### Database Operations
- **CRUD Operations**: Full Create, Read, Update, Delete for all entities
- **Advanced Search & Filter**: Multi-criteria querying with complex relationships
- **Pagination**: Efficient data retrieval for large datasets
- **Transactions**: Atomic operations with rollback capability
- **Data Validation**: Business rule enforcement at database level

### 5. Authentication & Security Layer

**Location**: `auth.py`

**Purpose**: Handles user authentication, authorization, and security

#### Authentication Components
- **LDAP Integration**: Corporate directory authentication with enhanced error handling
- **Flask-Login**: Session management and user state
- **User Model**: User representation and role management
- **Bypass Authentication**: Development/testing user accounts

#### Security Features
- **Role-Based Access Control**: Admin vs. regular user permissions
- **Session Security**: Secure cookie configuration
- **CSRF Protection**: Cross-site request forgery prevention
- **Input Validation**: XSS and injection attack prevention
- **File Upload Security**: Enhanced file type and size validation

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

### 3. Enhanced Form Submission Flow

```
Training Catalog Search → Form Population → Multi-Section Input → Optimized Validation → 
Essential Data Storage → Immediate Success Response → Background Processing
     ↓                                                           ↓
Success Page Display                                    File Upload → Email Notifications →
                                                       Related Data Storage → Complete Processing
```

**Performance Architecture**:
- **Optimized Client-Side Validation**: Cached DOM elements, batched operations, and requestAnimationFrame for smooth UI updates
- **Background Processing**: Non-essential operations (file uploads, email notifications, related data) processed asynchronously using ThreadPoolExecutor
- **Immediate User Response**: Users see success page within ~150ms while background tasks complete
- **Threaded Architecture**: 3-worker thread pool handles background operations without blocking user experience

## Component Interactions

### Core Dependencies

```
app.py (Main Application)
├── models.py (Enhanced Database Layer)
│   ├── TrainingForm
│   ├── Trainee
│   ├── TravelExpense
│   ├── MaterialExpense
│   ├── Attachment
│   ├── Admin
│   └── TrainingCatalog
├── forms.py (Enhanced Form Validation)
├── auth.py (Authentication)
├── utils.py (Utilities)
├── lookups.py (Data Services)
└── config.py (Configuration)
```

### External Dependencies

```
Flask Framework
├── SQLAlchemy (ORM with enhanced models)
├── Flask-Login (Session Management)
├── Flask-WTF (Form Handling with custom validators)
├── Werkzeug (WSGI Utilities)
└── Jinja2 (Template Engine)

Production WSGI Server & Background Processing
├── Waitress (Production WSGI Server)
├── ThreadPoolExecutor (Background task processing)
└── Concurrent.futures (Asynchronous form processing)

LDAP Integration
├── ldap3 (Enhanced LDAP Client)
└── Corporate LDAP Server

Microsoft Graph API Integration
├── microsoft_graph.py (Centralized Graph API client module)
├── requests (HTTP Client for API calls)
├── Azure App Registration (Service Principal Authentication)
└── Employee Directory Synchronization

File System
├── Environment-Specific Storage Organization
│   ├── Development: Local uploads/ folder
│   ├── Staging: Local uploads_staging/ folder
│   └── Production: Dedicated c:/TrainingAppData/Uploads/ folder
└── Network Storage (Legacy)

Frontend Enhancements
├── Bootstrap 5 (UI Framework)
├── Bootstrap Icons (Icon Library)
├── Flatpickr (Date Picker)
├── Optimized Form Validation (cached DOM elements, batched operations)
├── Custom CSS/JS Components
└── Profile Picture Management (profile-picture.js)
```

## Design Patterns

### 1. Model-View-Controller (MVC)
- **Models**: Enhanced database entities and business logic (`models.py`)
- **Views**: Progressive disclosure templates and components (`templates/`)
- **Controllers**: Route handlers and request processing (`app.py`)

### 2. Repository Pattern
- Database operations abstracted through enhanced model functions
- Consistent interface for data access across the application
- Transaction management and error handling centralized
- Support for complex queries and relationships

### 3. Factory Pattern
- Flask application factory for configuration management
- Database session factory for connection management
- Form factory for dynamic form generation with progressive disclosure

### 4. Decorator Pattern
- Authentication decorators for route protection
- Validation decorators for enhanced form processing
- Error handling decorators for consistent error responses

## Enhanced Features

### 1. User Interface Components

#### Approve Button System
- **Three-State Design**: Approved, Ready for Approval, and Needs Changes states with distinct visual indicators
- **Color-Coded Feedback**: Green for approve, red for unapprove, orange for needs changes
- **Icon Swapping**: Dynamic icon changes on hover for clear action indication  
- **HTMX Integration**: Asynchronous state updates without page refresh
- **Accessibility Compliant**: Proper color contrast and keyboard navigation support

#### Visual Validation Indicators
- **Flagged Value Highlighting**: Automatic visual highlighting of fields containing placeholder or incomplete values
- **Orange Border Styling**: Clean border indicators around flagged field rows maintaining layout integrity
- **"Needs Review" Tags**: Positioned indicators that appear adjacent to flagged fields for immediate identification
- **Smart Field Detection**: Automatic detection of common placeholder values ('1111', 'na', 'NA', 'N/A', 'Not sure', '€1111', '1111.00')
- **Template Macro System**: Reusable rendering macros for consistent flagged value display across views

#### CSS Architecture
- **Modular Organization**: CSS organized into logical sections for improved maintainability
- **Performance Optimized**: Optimized selectors and consolidated styles
- **Responsive Design**: Mobile-first approach with consistent spacing and typography
- **Modern Features**: CSS variables and modern features for flexibility and theming
- **Logo Styling**: White background container for Stryker logo visibility
- **Validation Styling**: Consistent color scheme for validation states with accessibility compliance

#### JavaScript Performance Optimizations
- **DOM Element Caching**: Form validation elements cached at initialization to eliminate repeated queries
- **Batched Operations**: Validation clearing and UI updates performed in batches using requestAnimationFrame
- **Optimized Query Selectors**: Scoped queries within form containers instead of document-wide searches
- **Streamlined Validation Logic**: Reduced conditional checks and simplified validation workflows
- **Smart JSON Parsing**: Cached JSON parsing for trainee data to eliminate redundant operations

### 2. Progressive Form Disclosure
- **Multi-Section Layout**: Training Details, Trainees, Travel Expenses, Material Expenses, Attachments
- **Dynamic Visibility**: Sections shown progressively in new form submissions based on user progress and selections
- **Edit Mode Display**: All sections visible immediately in edit mode for comprehensive data review and modification
- **Training Catalog Integration**: Quick form population from predefined courses
- **Enhanced User Experience**: Reduced cognitive load for new forms and complete visibility for edits

### 3. Advanced Data Management
- **Trainee Management**: Individual trainee records with department tracking
- **Expense Tracking**: Separate models for travel and material expenses
- **Enhanced Search**: Multi-field search with relationship traversal
- **Analytics Dashboard**: Leaderboard with training statistics
- **Soft Delete Management**: Forms can be soft deleted and recovered with 180-day retention
- **Delete Status Filtering**: Filter forms by delete status (not deleted, deleted, all)
- **Employee Data Management**: Database-driven employee directory with automated nightly synchronization from Microsoft Graph API using the `microsoft_graph.py` module

### 4. Enhanced File Management
- **Environment-Specific Storage**: Different upload folders per environment to prevent deployment conflicts
- **Form-Specific Organization**: Files organized by form ID within each environment
- **Metadata Tracking**: File descriptions and attachment details
- **Secure Access Control**: User-based file access permissions
- **Enhanced Export**: Multi-worksheet Excel exports with complete data

## Scalability Considerations

### Current Architecture Strengths
- **Modular Design**: Clear separation of concerns with enhanced modularity
- **Progressive Enhancement**: Frontend features degrade gracefully
- **Efficient Data Access**: Optimized queries with proper relationships
- **Caching Strategy**: Lookup data cached for performance

### Current Architecture Limitations
- **Monolithic Design**: Single application instance
- **SQLite Database**: File-based database for development
- **Local File Storage**: Limited to single server (development)
- **Session Storage**: In-memory session management

### Production Scalability Features
- **MariaDB Database**: Dedicated database server with relationship support
- **Waitress WSGI Server**: Production-grade WSGI server replacing Flask's development server
- **Environment-Specific File Storage**: Dedicated production folder outside project directory
- **LDAP Integration**: Centralized authentication
- **Stateless Design**: Session data stored externally

### Future Scalability Options
- **Microservices**: Split into focused services (Form Service, User Service, File Service)
- **Load Balancing**: Multiple application instances with session sharing
- **Caching Layer**: Redis or Memcached for enhanced performance
- **CDN Integration**: Static asset delivery optimization
- **Database Clustering**: High availability database setup with read replicas

## Security Architecture

### Authentication Security
- **Enhanced LDAP Integration**: Improved error handling and connection management
- **Session Management**: Secure session handling with configurable timeouts
- **Password Security**: No local password storage
- **Multi-Factor Authentication**: Ready for MFA integration

### Authorization Security
- **Enhanced Role-Based Access**: Admin and user role separation with granular permissions
- **Resource Protection**: Route-level and resource-level access control
- **Data Isolation**: User can only access own data with admin override
- **Audit Trail**: Comprehensive logging of admin actions

### Data Security
- **Enhanced Input Validation**: Comprehensive form validation with business rules
- **SQL Injection Prevention**: ORM-based database access with parameterized queries
- **XSS Protection**: Template-based output escaping
- **File Upload Security**: Enhanced type, size, and content validation

### Network Security
- **HTTPS Support**: SSL/TLS encryption ready with secure headers
- **CSRF Protection**: Enhanced cross-site request forgery prevention
- **Secure Headers**: Comprehensive security header configuration
- **Network Isolation**: Database and file server separation

## Performance Architecture

### Current Performance Features
- **Enhanced Database Indexing**: Optimized query performance with relationship indexes
- **Efficient Pagination**: Large dataset handling with relationship data
- **Advanced Caching**: Multi-level caching for lookup data and search results
- **Static Asset Optimization**: Minified CSS/JS with CDN readiness
- **Background Processing**: ThreadPoolExecutor-based asynchronous processing for non-essential operations
- **Optimized Client-Side Validation**: Cached DOM elements and batched operations for fast form submission
- **Immediate User Response**: Users see success page within ~150ms while background tasks complete

### Performance Monitoring
- **Comprehensive Logging**: Application, database, and user action logging
- **Error Tracking**: Exception monitoring and reporting with context
- **Database Monitoring**: Query performance tracking with relationship analysis
- **File Upload Monitoring**: Enhanced upload size and type tracking

### Future Optimization Opportunities
- **Database Query Optimization**: Advanced query analysis and tuning
- **Caching Strategy**: Redis-based caching implementation with invalidation
- **Asset Optimization**: CDN and compression with resource bundling
- **Queue-Based Processing**: Redis/Celery for more complex background task management
- **Progressive Loading**: Lazy loading for large datasets and file lists 
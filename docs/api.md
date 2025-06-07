# API Reference Documentation

## Overview

The Flask Survey Form System provides both web interface routes and RESTful API endpoints for data access and manipulation. All endpoints require authentication and implement proper authorization controls.

## Authentication

### Authentication Methods
- **Session-based**: Primary authentication method using Flask-Login
- **LDAP Integration**: Corporate directory authentication
- **CSRF Protection**: All POST requests require CSRF tokens

### Authorization Levels
- **Public**: No authentication required (login page only)
- **User**: Authenticated user access
- **Admin**: Administrative privileges required

## Web Interface Routes

### Authentication Routes

#### POST /login
**Purpose**: User authentication via LDAP

**Authentication**: None (public endpoint)

**Request**:
```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=user@domain.com&password=userpassword&csrf_token=...
```

**Response**:
- **Success**: Redirect to dashboard or requested page
- **Failure**: Redirect to login with error message

**Form Fields**:
- `username`: User email address
- `password`: User password
- `csrf_token`: CSRF protection token

#### GET /logout
**Purpose**: User session termination

**Authentication**: User

**Response**: Redirect to login page

### Home and Navigation Routes

#### GET /
**Purpose**: Application home/dashboard page

**Authentication**: User

**Response**: HTML home dashboard with navigation options

**Features**:
- User-specific content based on role
- Quick access to form submission
- Recent activity overview

#### GET /new
**Purpose**: Display new training form submission interface with progressive disclosure

**Authentication**: User

**Response**: HTML form for training submission

**Features**:
- Training catalog search and selection
- Progressive form disclosure with multi-section layout (new forms only)
- Dynamic form validation based on training type
- Employee lookup integration with autocomplete
- Enhanced file upload interface with form-specific organization
- Multi-section layout:
  - Training Catalog Search
  - Training Details
  - Add Trainees
  - Travel Expenses
  - Material Expenses
  - Attachments

### Form Management Routes

#### POST /submit
**Purpose**: Process enhanced training form submission with new fields and related data

**Authentication**: User

**Request**:
```http
POST /submit
Content-Type: multipart/form-data

training_type=External+Training&
training_name=Python+Programming+Fundamentals&
supplier_name=Training+Corp&
location_type=Offsite&
location_details=Conference+Center&
start_date=2024-01-15&
end_date=2024-01-16&
training_hours=16.0&
training_description=Advanced+Skills+Training&
course_cost=1500.00&
invoice_number=INV-2024-001&
trainer_email=trainer@company.com&
ida_class=Class+B+-+Nat%2FInternational+Industry+Cert&
attachments=@file1.pdf&
trainees_data=[{"email":"user1@company.com","name":"John Doe","department":"Engineering"}]&
csrf_token=...
```

**Response**:
- **Success**: Redirect to success page
- **Validation Error**: Return form with error messages

**Enhanced Form Processing**:
- File upload handling with form-specific organization (`uploads/form_ID/`)
- Trainee data processing and validation
- Travel and material expense handling with full CRUD operations
- Enhanced data validation with conditional requirements
- Database storage with relationship management
- Email notifications

**New Required Fields**:
- `training_name`: Name/title of the training course (always required)
- `trainer_email`: Email of trainer (captured for internal training)
- `invoice_number`: Invoice number (required for external training)
- `ida_class`: Training classification (Class A-D)

#### GET /edit/<int:form_id>
**Purpose**: Display enhanced form editing interface

**Authentication**: User (own forms) or Admin

**Parameters**:
- `form_id`: Training form ID to edit

**Response**: HTML form pre-populated with existing data including new fields

**Authorization**:
- Users can only edit their own unapproved forms
- Admins can edit any form

**Enhanced Features**:
- Full form display in edit mode (all sections visible immediately)
- All new fields properly loaded and editable
- Trainee management in edit mode with pre-populated data
- Travel expenses pre-populated and editable
- Material expenses pre-populated and editable
- File attachment management
- Enhanced JSON data handling to prevent truncation issues

#### POST /edit/<int:form_id>
**Purpose**: Update existing training form with enhanced data

**Authentication**: User (own forms) or Admin

**Parameters**:
- `form_id`: Training form ID to update

**Request**: Same format as POST /submit with enhanced fields

**Response**:
- **Success**: Redirect to form view
- **Error**: Return form with error messages

#### GET /view/<int:form_id>
**Purpose**: Display comprehensive training form details with all related data including soft delete management

**Authentication**: User

**Parameters**:
- `form_id`: Training form ID to view

**Response**: HTML page with complete form details

**Enhanced Features**:
- Read-only form display with all new fields
- Comprehensive trainee list with department information
- Travel and material expense details (when implemented)
- Enhanced attachment display with descriptions
- Form-specific file organization
- Approval status and admin controls
- Delete/recover button functionality with permission checks
- Visual indicators for deleted forms with red "DELETED" badges
- **Flagged Value Detection**: Automatic highlighting of fields containing placeholder or incomplete values
- **Visual Quality Indicators**: Orange border styling and "Needs Review" tags for flagged fields
- **Data Quality Assurance**: Clear identification of fields requiring reviewer attention

### Data Management Routes

#### GET /list
**Purpose**: Display training submissions with enhanced search and filter capabilities including soft delete management

**Authentication**: User

**Query Parameters**:
- `search`: Enhanced search across training name, description, trainer name, trainer email, supplier name
- `date_from`: Start date filter (YYYY-MM-DD)
- `date_to`: End date filter (YYYY-MM-DD)
- `training_type`: Filter by training type
- `approval_status`: Filter by approval status (approved, unapproved)
- `delete_status`: **NEW**: Filter by delete status ("" for not deleted, "deleted" for deleted, "all" for all forms)
- `sort_by`: Sort field (submission_date, start_date, end_date, cost, training_name)
- `sort_order`: Sort direction (ASC, DESC)
- `page`: Page number for pagination

**Response**: HTML page with filtered and paginated results

**Enhanced Search Capabilities**:
- Training name prioritized in search
- Trainer email included in search
- Improved result relevance
- **NEW**: Soft delete status filtering with default to show only non-deleted forms

**Example**:
```http
GET /list?search=python&date_from=2024-01-01&training_type=External+Training&approval_status=approved&delete_status=&sort_by=training_name&sort_order=ASC&page=1
```

#### GET /my_submissions
**Purpose**: Display current user's training submissions with enhanced filtering including soft delete management

**Authentication**: User

**Query Parameters**: Same as /list including the new delete_status parameter

**Response**: HTML page with user's submissions only

**Enhanced Features**:
- Personal submission history
- Status tracking for user's forms
- Quick access to edit unapproved forms
- **NEW**: View deleted forms with recovery option

#### GET /leaderboard
**Purpose**: Display training statistics, analytics, and leaderboard

**Authentication**: User

**Response**: HTML page with comprehensive training statistics

**Enhanced Features**:
- Total submissions by user with training names
- Training hours summary and trends
- Cost analysis with breakdowns
- Monthly/quarterly statistics
- Top trainees by training hours
- Department-wise analytics
- Training type distribution
- Trainer participation statistics

### Administrative Routes

#### GET /manage_admins
**Purpose**: Enhanced admin user management interface

**Authentication**: Admin

**Response**: HTML page with admin user list and management controls

**Features**:
- Add/remove admin users
- Admin user information display
- Role management interface

#### POST /manage_admins
**Purpose**: Add or remove admin users with enhanced validation

**Authentication**: Admin

**Request**:
```http
POST /manage_admins
Content-Type: application/x-www-form-urlencoded

# Add admin
add_admin=1&email=newadmin@company.com&first_name=John&last_name=Doe&csrf_token=...

# Remove admin
remove_admin=admin@company.com&csrf_token=...
```

**Response**: Redirect to admin management page with status message

#### GET /approve/<int:form_id>
**Purpose**: Approve training form submission with comprehensive logging

**Authentication**: Admin

**Parameters**:
- `form_id`: Training form ID to approve

**Response**: Redirect to form view with approval confirmation

**Features**:
- Comprehensive audit logging
- Email notifications (future feature)
- Approval timestamp tracking
- Approve button UI with state indication:
  - **Approved forms**: Show "Approved" text, hover shows "Unapprove" with red background
  - **Ready for approval**: Show "Unapproved" text, hover shows "Approve" with green background  
  - **Not ready for approval**: Show "Unapproved" text, hover shows "Needs Changes" with orange background

#### POST /delete/<int:form_id>
**Purpose**: **NEW**: Soft delete a training form submission (marks as deleted for 180 days)

**Authentication**: Admin or form submitter

**Parameters**:
- `form_id`: Training form ID to delete

**Request**:
```http
POST /delete/123
Content-Type: application/x-www-form-urlencoded

csrf_token=...
```

**Response**: Redirect to form list with deletion confirmation

**Features**:
- Soft delete implementation (form retained for 180 days)
- Only admin users or form submitters can delete
- Deleted forms remain in database with deleted flag and timestamp
- Forms can be recovered using the recover endpoint

#### POST /recover/<int:form_id>
**Purpose**: **NEW**: Recover a soft-deleted training form submission

**Authentication**: Admin or form submitter

**Parameters**:
- `form_id`: Training form ID to recover

**Request**:
```http
POST /recover/123
Content-Type: application/x-www-form-urlencoded

csrf_token=...
```

**Response**: Redirect to form view with recovery confirmation

**Features**:
- Restores deleted forms by removing deleted flag and timestamp
- Only admin users or form submitters can recover
- Recovered forms return to normal active status

### Utility Routes

#### GET /success
**Purpose**: Display enhanced form submission success page

**Authentication**: User

**Response**: HTML success confirmation page

**Features**:
- Confirmation of submission
- Next steps information
- Link to view submitted form

## API Endpoints

### Data Lookup APIs

#### GET /api/employees
**Purpose**: Enhanced employee directory lookup for autocomplete

**Authentication**: User

**Response**:
```json
[
  {
    "displayName": "John Doe",
    "email": "john.doe@company.com",
    "name": "John Doe",
    "department": "Engineering",
    "firstName": "John",
    "lastName": "Doe"
  },
  ...
]
```

**Enhanced Features**:
- Cached for performance optimization
- Comprehensive employee data
- Department information included
- Optimized search performance

#### GET /api/lookup/<string:entity_type>
**Purpose**: Enhanced generic lookup service for various entity types

**Authentication**: User

**Parameters**:
- `entity_type`: Type of entity to lookup (employees, trainings)

**Response**:
```json
// For entity_type = "trainings"
[
  {
    "id": 1,
    "training_name": "Python Programming Fundamentals",
    "area": "Software Development",
    "training_desc": "Comprehensive Python programming course",
    "ida_class": "Class B - Nat/International Industry Cert",
    "training_type": "External Training",
    "supplier_name": "Tech Training Corp",
    "training_hours": 16.0,
    "course_cost": 1500.0,
    "challenge_lvl": "Intermediate",
    "skill_impact": "High"
  },
  ...
]
```

**Enhanced Features**:
- Comprehensive training catalog data
- Enhanced search capabilities
- Rich metadata for training selection

#### GET /api/export_claim5_options
**Purpose**: Get available options for enhanced Claim 5 export

**Authentication**: User

**Response**:
```json
{
  "quarters": [
    {"value": "2024-Q1", "label": "Q1 2024"},
    {"value": "2024-Q2", "label": "Q2 2024"},
    ...
  ],
  "years": [2023, 2024, 2025],
  "approved_forms_count": 45,
  "total_training_hours": 720,
  "total_cost": 75000.00
}
```

**Enhanced Features**:
- Additional statistical information
- Training hours and cost summaries
- Enhanced filtering options

### File Management APIs

#### GET /uploads/<path:filename>
**Purpose**: Secure file download with enhanced organization and access control

**Authentication**: User

**Parameters**:
- `filename`: Secure filename path including form organization (e.g., "form_123/20240115_143022_certificate.pdf")

**Response**: File content with appropriate headers

**Enhanced Security**:
- Form-based file organization validation
- Enhanced access control (users can only access files from their forms or approved forms)
- Secure file serving with path validation
- Audit logging for file access

**File Path Structure**:
```
uploads/form_123/20240115_143022_certificate.pdf
uploads/form_124/20240116_091234_invoice.pdf
```

#### POST /export_claim5
**Purpose**: Generate and download enhanced Claim 5 Excel export

**Authentication**: User

**Request**:
```http
POST /export_claim5
Content-Type: application/x-www-form-urlencoded

quarter=2024-Q1&csrf_token=...
```

**Response**: Enhanced Excel file download with multiple worksheets

**Enhanced Features**:
- Filtered by quarter with enhanced date handling
- Only approved forms included
- Formatted for Claim 5 requirements
- Multiple comprehensive worksheets:
  - Summary with totals and statistics
  - Training details with all new fields
  - Trainee information with departments
  - Travel expenses (when implemented)
  - Material expenses (when implemented)
- Enhanced formatting and data validation

## Error Handling

### HTTP Status Codes

- **200 OK**: Successful request
- **302 Found**: Redirect response
- **400 Bad Request**: Invalid request data or validation errors
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient privileges
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Error Response Format

**HTML Responses** (Web Interface):
- Error messages displayed via Flask flash messages
- Enhanced form validation errors shown inline with context
- Redirect to appropriate error pages
- User-friendly error explanations

**JSON Responses** (API Endpoints):
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Specific field error",
    "context": "Additional error context"
  }
}
```

### Common Error Scenarios

#### Authentication Errors
- **401 Unauthorized**: User not logged in
- **403 Forbidden**: Insufficient privileges for admin routes
- **LDAP Connection**: Enhanced LDAP error handling with user-friendly messages

#### Validation Errors
- **400 Bad Request**: Enhanced form validation failures with specific field guidance
- **400 Bad Request**: File upload validation (type, size, organization)
- **400 Bad Request**: Missing required fields with conditional validation
- **Trainee Validation**: Invalid trainee data format or missing information

#### Resource Errors
- **404 Not Found**: Training form not found
- **404 Not Found**: File not found in form-specific organization
- **403 Forbidden**: Access denied to resource (enhanced authorization)

## Rate Limiting and Security

### Security Headers
- **CSRF Protection**: Enhanced CSRF tokens for all forms
- **Secure Cookies**: Session cookies with secure flags and proper configuration
- **Content Security Policy**: XSS protection headers
- **File Upload Security**: Enhanced file type and content validation

### Input Validation
- **Enhanced Form Validation**: Server-side validation for all inputs with business logic
- **File Validation**: Strict type, size, and organization restrictions
- **SQL Injection Prevention**: ORM-based queries only with parameterized statements
- **Conditional Validation**: Dynamic validation based on form state

### Access Control
- **Authentication Required**: All routes except login
- **Enhanced Role-Based Access**: Admin routes with granular permissions
- **Resource Ownership**: Users can only access own data with admin override
- **File Access Control**: Form-specific file access with enhanced security

## Usage Examples

### JavaScript API Usage

#### Enhanced Employee Lookup
```javascript
fetch('/api/employees')
  .then(response => response.json())
  .then(employees => {
    // Populate enhanced autocomplete dropdown
    employees.forEach(emp => {
      console.log(`${emp.displayName} (${emp.email}) - ${emp.department}`);
    });
  });
```

#### Enhanced Form Submission
```javascript
const formData = new FormData();
formData.append('training_type', 'External Training');
formData.append('training_name', 'Python Programming Fundamentals');
formData.append('supplier_name', 'Training Corp');
formData.append('start_date', '2024-01-15');
formData.append('end_date', '2024-01-16');
formData.append('training_hours', '16.0');
formData.append('course_cost', '1500.00');
formData.append('invoice_number', 'INV-2024-001');
formData.append('ida_class', 'Class B - Nat/International Industry Cert');
formData.append('trainees_data', JSON.stringify([
  {"email": "user1@company.com", "name": "John Doe", "department": "Engineering"}
]));
formData.append('csrf_token', getCsrfToken());

fetch('/submit', {
  method: 'POST',
  body: formData
})
.then(response => {
  if (response.redirected) {
    window.location.href = response.url;
  }
});
```

#### Enhanced Training Catalog Lookup
```javascript
fetch('/api/lookup/trainings')
  .then(response => response.json())
  .then(trainings => {
    // Filter and display enhanced training options
    const filtered = trainings.filter(t => 
      t.training_type === 'External Training' && t.skill_impact === 'High'
    );
    
    // Populate form with selected training
    if (selectedTraining) {
      document.getElementById('training_name').value = selectedTraining.training_name;
      document.getElementById('training_hours').value = selectedTraining.training_hours;
      document.getElementById('course_cost').value = selectedTraining.course_cost;
      document.getElementById('ida_class').value = selectedTraining.ida_class;
    }
  });
```

### cURL Examples

#### Login
```bash
curl -X POST http://localhost:5000/login \
  -d "username=user@company.com&password=password&csrf_token=..." \
  -c cookies.txt
```

#### Get Enhanced Employee List
```bash
curl -X GET http://localhost:5000/api/employees \
  -b cookies.txt \
  -H "Accept: application/json"
```

#### Submit Enhanced Training Form
```bash
curl -X POST http://localhost:5000/submit \
  -b cookies.txt \
  -F "training_type=External Training" \
  -F "training_name=Python Programming Fundamentals" \
  -F "supplier_name=Training Corp" \
  -F "start_date=2024-01-15" \
  -F "end_date=2024-01-16" \
  -F "training_hours=16.0" \
  -F "course_cost=1500.00" \
  -F "invoice_number=INV-2024-001" \
  -F "ida_class=Class B - Nat/International Industry Cert" \
  -F "attachments=@training_cert.pdf" \
  -F "trainees_data=[{\"email\":\"user1@company.com\",\"name\":\"John Doe\",\"department\":\"Engineering\"}]" \
  -F "csrf_token=..."
```

## API Versioning and Compatibility

### Current Version
- **Version**: 1.0
- **Stability**: Stable
- **Backward Compatibility**: Maintained for web interface routes
- **Enhanced Features**: New fields and functionality added with backward compatibility

### Future Considerations
- **REST API**: Potential future REST API implementation with comprehensive endpoints
- **API Versioning**: URL-based versioning (/api/v1/) for future versions
- **OpenAPI Specification**: Swagger documentation for enhanced API documentation
- **Rate Limiting**: Request throttling for API endpoints
- **Webhook Support**: Future webhook integration for notifications
- **Real-time Updates**: WebSocket support for real-time form status updates 
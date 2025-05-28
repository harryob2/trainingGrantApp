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

### Form Management Routes

#### GET /
**Purpose**: Application dashboard/home page

**Authentication**: User

**Response**: HTML dashboard with navigation options

**Features**:
- User-specific content based on role
- Quick access to form submission
- Recent submissions summary

#### GET /submit
**Purpose**: Display training form submission interface

**Authentication**: User

**Response**: HTML form for training submission

**Features**:
- Dynamic form validation
- Employee lookup integration
- Training catalog autocomplete
- File upload interface

#### POST /submit
**Purpose**: Process training form submission

**Authentication**: User

**Request**:
```http
POST /submit
Content-Type: multipart/form-data

training_type=External+Training&
supplier_name=Training+Corp&
location_type=Offsite&
location_details=Conference+Center&
start_date=2024-01-15&
end_date=2024-01-16&
training_description=Advanced+Skills+Training&
course_cost=1500.00&
attachments=@file1.pdf&
trainees_data=[{"email":"user1@company.com","name":"John Doe"}]&
csrf_token=...
```

**Response**:
- **Success**: Redirect to success page
- **Validation Error**: Return form with error messages

**Form Processing**:
- File upload handling
- Data validation
- Database storage
- Email notifications

#### GET /edit/<int:form_id>
**Purpose**: Display form editing interface

**Authentication**: User (own forms) or Admin

**Parameters**:
- `form_id`: Training form ID to edit

**Response**: HTML form pre-populated with existing data

**Authorization**:
- Users can only edit their own unapproved forms
- Admins can edit any form

#### POST /edit/<int:form_id>
**Purpose**: Update existing training form

**Authentication**: User (own forms) or Admin

**Parameters**:
- `form_id`: Training form ID to update

**Request**: Same format as POST /submit

**Response**:
- **Success**: Redirect to form view
- **Error**: Return form with error messages

#### GET /view/<int:form_id>
**Purpose**: Display training form details

**Authentication**: User

**Parameters**:
- `form_id`: Training form ID to view

**Response**: HTML page with form details and attachments

**Features**:
- Read-only form display
- Attachment download links
- Approval status
- Admin approval controls (for admins)

### Data Management Routes

#### GET /list
**Purpose**: Display training submissions with search and filter

**Authentication**: User

**Query Parameters**:
- `search`: Search term for text fields
- `date_from`: Start date filter (YYYY-MM-DD)
- `date_to`: End date filter (YYYY-MM-DD)
- `training_type`: Filter by training type
- `sort_by`: Sort field (submission_date, start_date, end_date, cost)
- `sort_order`: Sort direction (ASC, DESC)
- `page`: Page number for pagination

**Response**: HTML page with filtered and paginated results

**Example**:
```http
GET /list?search=python&date_from=2024-01-01&training_type=External+Training&sort_by=start_date&sort_order=DESC&page=2
```

#### GET /my_submissions
**Purpose**: Display current user's training submissions

**Authentication**: User

**Query Parameters**: Same as /list

**Response**: HTML page with user's submissions only

#### GET /leaderboard
**Purpose**: Display training statistics and leaderboard

**Authentication**: User

**Response**: HTML page with training statistics

**Features**:
- Total submissions by user
- Training hours summary
- Cost analysis
- Monthly/quarterly breakdowns

### Administrative Routes

#### GET /manage_admins
**Purpose**: Admin user management interface

**Authentication**: Admin

**Response**: HTML page with admin user list and management controls

#### POST /manage_admins
**Purpose**: Add or remove admin users

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
**Purpose**: Approve training form submission

**Authentication**: Admin

**Parameters**:
- `form_id`: Training form ID to approve

**Response**: Redirect to form view with approval confirmation

## API Endpoints

### Data Lookup APIs

#### GET /api/employees
**Purpose**: Employee directory lookup for autocomplete

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

**Features**:
- Cached for performance
- Filtered employee list
- Department information included

#### GET /api/lookup/<string:entity_type>
**Purpose**: Generic lookup service for various entity types

**Authentication**: User

**Parameters**:
- `entity_type`: Type of entity to lookup (employees, trainings)

**Response**:
```json
// For entity_type = "trainings"
[
  {
    "id": 1,
    "name": "Python Programming",
    "area": "Software Development",
    "ida_class": "Class B - Nat/International Industry Cert",
    "training_type": "External Training",
    "supplier_name": "Tech Training Corp",
    "training_hours": 16.0
  },
  ...
]
```

#### GET /api/export_claim5_options
**Purpose**: Get available options for Claim 5 export

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
  "approved_forms_count": 45
}
```

### File Management APIs

#### GET /uploads/<path:filename>
**Purpose**: Secure file download

**Authentication**: User

**Parameters**:
- `filename`: Secure filename of uploaded file

**Response**: File content with appropriate headers

**Security**:
- Filename validation
- Access control (users can only access files from their forms or approved forms)
- Secure file serving

#### POST /export_claim5
**Purpose**: Generate and download Claim 5 Excel export

**Authentication**: User

**Request**:
```http
POST /export_claim5
Content-Type: application/x-www-form-urlencoded

quarter=2024-Q1&csrf_token=...
```

**Response**: Excel file download

**Features**:
- Filtered by quarter
- Only approved forms included
- Formatted for Claim 5 requirements
- Multiple worksheets (summary and details)

## Error Handling

### HTTP Status Codes

- **200 OK**: Successful request
- **302 Found**: Redirect response
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient privileges
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Error Response Format

**HTML Responses** (Web Interface):
- Error messages displayed via Flask flash messages
- Form validation errors shown inline
- Redirect to appropriate error pages

**JSON Responses** (API Endpoints):
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Specific field error"
  }
}
```

### Common Error Scenarios

#### Authentication Errors
- **401 Unauthorized**: User not logged in
- **403 Forbidden**: Insufficient privileges for admin routes

#### Validation Errors
- **400 Bad Request**: Form validation failures
- **400 Bad Request**: Invalid file uploads
- **400 Bad Request**: Missing required fields

#### Resource Errors
- **404 Not Found**: Training form not found
- **404 Not Found**: File not found
- **403 Forbidden**: Access denied to resource

## Rate Limiting and Security

### Security Headers
- **CSRF Protection**: All forms include CSRF tokens
- **Secure Cookies**: Session cookies with secure flags
- **Content Security Policy**: XSS protection headers

### Input Validation
- **Form Validation**: Server-side validation for all inputs
- **File Validation**: Type and size restrictions
- **SQL Injection Prevention**: ORM-based queries only

### Access Control
- **Authentication Required**: All routes except login
- **Role-Based Access**: Admin routes restricted
- **Resource Ownership**: Users can only access own data

## Usage Examples

### JavaScript API Usage

#### Employee Lookup
```javascript
fetch('/api/employees')
  .then(response => response.json())
  .then(employees => {
    // Populate autocomplete dropdown
    employees.forEach(emp => {
      console.log(`${emp.displayName} (${emp.email})`);
    });
  });
```

#### Form Submission
```javascript
const formData = new FormData();
formData.append('training_type', 'External Training');
formData.append('supplier_name', 'Training Corp');
formData.append('start_date', '2024-01-15');
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

#### Training Catalog Lookup
```javascript
fetch('/api/lookup/trainings')
  .then(response => response.json())
  .then(trainings => {
    // Filter and display training options
    const filtered = trainings.filter(t => 
      t.training_type === 'External Training'
    );
  });
```

### cURL Examples

#### Login
```bash
curl -X POST http://localhost:5000/login \
  -d "username=user@company.com&password=password&csrf_token=..." \
  -c cookies.txt
```

#### Get Employee List
```bash
curl -X GET http://localhost:5000/api/employees \
  -b cookies.txt \
  -H "Accept: application/json"
```

#### Submit Training Form
```bash
curl -X POST http://localhost:5000/submit \
  -b cookies.txt \
  -F "training_type=External Training" \
  -F "supplier_name=Training Corp" \
  -F "start_date=2024-01-15" \
  -F "attachments=@training_cert.pdf" \
  -F "csrf_token=..."
```

## API Versioning and Compatibility

### Current Version
- **Version**: 1.0
- **Stability**: Stable
- **Backward Compatibility**: Maintained for web interface routes

### Future Considerations
- **REST API**: Potential future REST API implementation
- **API Versioning**: URL-based versioning (/api/v1/)
- **OpenAPI Specification**: Swagger documentation
- **Rate Limiting**: Request throttling for API endpoints 
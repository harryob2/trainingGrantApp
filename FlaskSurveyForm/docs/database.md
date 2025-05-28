# Database Schema Documentation

## Overview

The Flask Survey Form System uses SQLAlchemy ORM for database operations with support for both SQLite (development) and MariaDB (production). The database schema is designed to handle training form submissions, file attachments, user administration, and training catalog management.

## Database Configuration

### Development Environment
- **Database Type**: SQLite
- **File Location**: `training_forms.db`
- **Connection**: Local file-based database
- **Advantages**: Easy setup, no server required, portable

### Production Environment
- **Database Type**: MariaDB/MySQL
- **Server**: `azulimpbi01`
- **Port**: `3306`
- **Database Name**: `analysis`
- **Connection**: Network-based database server
- **Advantages**: Multi-user support, better performance, backup capabilities

## Database Models

### 1. TrainingForm (training_forms)

**Purpose**: Core entity storing training submission data

**Table Structure**:
```sql
CREATE TABLE training_forms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    training_type VARCHAR NOT NULL,
    trainer_name VARCHAR,
    supplier_name VARCHAR,
    location_type VARCHAR NOT NULL,
    location_details VARCHAR,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    training_hours FLOAT,
    trainees_data TEXT,
    submission_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved BOOLEAN DEFAULT FALSE,
    concur_claim VARCHAR,
    travel_cost FLOAT DEFAULT 0,
    food_cost FLOAT DEFAULT 0,
    materials_cost FLOAT DEFAULT 0,
    other_cost FLOAT DEFAULT 0,
    other_expense_description TEXT,
    course_cost FLOAT DEFAULT 0,
    training_description TEXT NOT NULL,
    submitter VARCHAR,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ida_class VARCHAR
);
```

**Field Descriptions**:
- `id`: Primary key, auto-incrementing unique identifier
- `training_type`: Type of training ("Internal Training" or "External Training")
- `trainer_name`: Name of trainer (required for internal training)
- `supplier_name`: Training supplier (required for external training)
- `location_type`: Training location ("Onsite", "Offsite", or "Virtual")
- `location_details`: Specific location details (required for offsite)
- `start_date`: Training start date
- `end_date`: Training end date
- `training_hours`: Duration in hours (required for internal training)
- `trainees_data`: JSON string containing trainee information
- `submission_date`: When the form was submitted
- `approved`: Admin approval status
- `concur_claim`: Concur expense claim number
- `travel_cost`: Travel expenses amount
- `food_cost`: Food and accommodation expenses
- `materials_cost`: Training materials cost
- `other_cost`: Other miscellaneous expenses
- `other_expense_description`: Description of other expenses
- `course_cost`: Course fee (required for external training)
- `training_description`: Detailed training description
- `submitter`: Email of the person who submitted the form
- `created_at`: Record creation timestamp
- `ida_class`: Training classification (Class A-D)

**Business Rules**:
- Internal training requires `trainer_name` and `training_hours`
- External training requires `supplier_name` and `course_cost`
- Offsite training requires `location_details`
- Virtual training requires attachments
- Other expenses require description when amount > 0

### 2. Attachment (attachments)

**Purpose**: Stores metadata for file attachments linked to training forms

**Table Structure**:
```sql
CREATE TABLE attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_id INTEGER NOT NULL,
    filename VARCHAR NOT NULL,
    description VARCHAR,
    FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE
);
```

**Field Descriptions**:
- `id`: Primary key, auto-incrementing unique identifier
- `form_id`: Foreign key reference to training_forms.id
- `filename`: Secure filename of the uploaded file
- `description`: Optional description of the attachment

**Relationships**:
- Many-to-One with TrainingForm (one form can have multiple attachments)
- Cascade delete (attachments deleted when form is deleted)

### 3. Admin (admins)

**Purpose**: Stores administrative user information

**Table Structure**:
```sql
CREATE TABLE admins (
    email VARCHAR PRIMARY KEY,
    first_name VARCHAR,
    last_name VARCHAR
);
```

**Field Descriptions**:
- `email`: Primary key, admin's email address
- `first_name`: Admin's first name
- `last_name`: Admin's last name

**Business Rules**:
- Email must be unique
- Used for role-based access control
- Integrated with LDAP authentication

### 4. TrainingCatalog (training_catalog)

**Purpose**: Predefined training courses for autocomplete and standardization

**Table Structure**:
```sql
CREATE TABLE training_catalog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area VARCHAR,
    training_name VARCHAR,
    qty_staff_attending VARCHAR,
    training_desc VARCHAR,
    challenge_lvl VARCHAR,
    skill_impact VARCHAR,
    evaluation_method VARCHAR,
    ida_class VARCHAR,
    training_type VARCHAR,
    training_hours FLOAT,
    supplier_name VARCHAR,
    course_cost FLOAT
);
```

**Field Descriptions**:
- `id`: Primary key, auto-incrementing unique identifier
- `area`: Training area or department
- `training_name`: Name of the training course
- `qty_staff_attending`: Expected number of attendees
- `training_desc`: Detailed training description
- `challenge_lvl`: Difficulty level of the training
- `skill_impact`: Expected skill improvement impact
- `evaluation_method`: How training effectiveness is measured
- `ida_class`: Training classification (Class A-D)
- `training_type`: Internal or External training
- `training_hours`: Standard duration in hours
- `supplier_name`: Training provider name
- `course_cost`: Standard cost for the training

## Database Relationships

### Entity Relationship Diagram

```
TrainingForm (1) ←→ (Many) Attachment
     ↓
   Submitter (User via LDAP)
     ↓
   Admin (Role-based access)

TrainingCatalog (Lookup data for forms)
```

### Relationship Details

1. **TrainingForm ↔ Attachment** (One-to-Many)
   - One training form can have multiple attachments
   - Attachments are deleted when the parent form is deleted (CASCADE)
   - Foreign key: `attachments.form_id → training_forms.id`

2. **User ↔ TrainingForm** (One-to-Many via submitter field)
   - One user can submit multiple training forms
   - User identification through email address
   - No direct foreign key (users managed via LDAP)

3. **Admin ↔ User** (Role assignment)
   - Admin table defines which users have administrative privileges
   - Used for authorization checks throughout the application

## Database Operations

### Core CRUD Operations

#### Create Operations
```python
# Insert new training form
def insert_training_form(form_data):
    with db_session() as session:
        form = TrainingForm(**form_data)
        session.add(form)
        session.flush()
        return form.id

# Add admin user
def add_admin(admin_data):
    with db_session() as session:
        admin = Admin(**admin_data)
        session.add(admin)
        return True
```

#### Read Operations
```python
# Get training form by ID
def get_training_form(form_id):
    with db_session() as session:
        return session.query(TrainingForm).filter_by(id=form_id).first()

# Get all forms with filtering
def get_all_training_forms(search_term="", date_from=None, date_to=None, 
                          training_type=None, sort_by="submission_date", 
                          sort_order="DESC", page=1):
    # Complex query with filtering, sorting, and pagination
```

#### Update Operations
```python
# Update training form
def update_training_form(form_id, form_data):
    with db_session() as session:
        form = session.query(TrainingForm).filter_by(id=form_id).first()
        if form:
            for key, value in form_data.items():
                setattr(form, key, value)
```

#### Delete Operations
```python
# Delete handled through CASCADE relationships
# When TrainingForm is deleted, associated Attachments are automatically deleted
```

### Advanced Query Operations

#### Search and Filter
```python
# Multi-criteria search
query = session.query(TrainingForm)

if search_term:
    query = query.filter(
        or_(
            TrainingForm.training_description.contains(search_term),
            TrainingForm.trainer_name.contains(search_term),
            TrainingForm.supplier_name.contains(search_term)
        )
    )

if date_from:
    query = query.filter(TrainingForm.start_date >= date_from)

if date_to:
    query = query.filter(TrainingForm.end_date <= date_to)

if training_type:
    query = query.filter(TrainingForm.training_type == training_type)
```

#### Pagination
```python
# Efficient pagination for large datasets
page_size = 10
offset = (page - 1) * page_size
forms = query.offset(offset).limit(page_size).all()
total_count = query.count()
```

#### Aggregation Queries
```python
# Training statistics for leaderboard
def get_training_statistics():
    with db_session() as session:
        stats = session.query(
            TrainingForm.submitter,
            func.count(TrainingForm.id).label('total_submissions'),
            func.sum(TrainingForm.training_hours).label('total_hours'),
            func.sum(TrainingForm.course_cost + TrainingForm.travel_cost + 
                    TrainingForm.food_cost + TrainingForm.materials_cost + 
                    TrainingForm.other_cost).label('total_cost')
        ).group_by(TrainingForm.submitter).all()
```

## Data Validation and Constraints

### Database-Level Constraints
- **NOT NULL**: Required fields enforced at database level
- **DEFAULT VALUES**: Automatic default values for optional fields
- **FOREIGN KEY**: Referential integrity for relationships
- **CASCADE DELETE**: Automatic cleanup of related records

### Application-Level Validation
- **Form Validation**: WTForms validators for user input
- **Business Rules**: Custom validation logic in form classes
- **Data Type Validation**: Automatic type conversion and validation
- **File Validation**: File type and size constraints

## Performance Considerations

### Indexing Strategy
```sql
-- Recommended indexes for performance
CREATE INDEX idx_training_forms_submitter ON training_forms(submitter);
CREATE INDEX idx_training_forms_submission_date ON training_forms(submission_date);
CREATE INDEX idx_training_forms_start_date ON training_forms(start_date);
CREATE INDEX idx_training_forms_approved ON training_forms(approved);
CREATE INDEX idx_attachments_form_id ON attachments(form_id);
```

### Query Optimization
- **Pagination**: Limit result sets to manageable sizes
- **Selective Loading**: Only load required fields for list views
- **Eager Loading**: Load related data in single queries when needed
- **Connection Pooling**: Reuse database connections efficiently

### Caching Strategy
- **Lookup Data**: Cache training catalog and employee data
- **Session Data**: Cache user session information
- **Query Results**: Cache frequently accessed data

## Backup and Recovery

### Development Environment
- **SQLite File Backup**: Simple file copy for backup
- **Version Control**: Database schema tracked in git
- **Migration Scripts**: Database changes managed through migrations

### Production Environment
- **Automated Backups**: Regular database dumps
- **Point-in-Time Recovery**: Transaction log backups
- **Disaster Recovery**: Off-site backup storage
- **Data Retention**: Configurable retention policies

## Migration Management

### Schema Changes
```python
# Example migration for adding new field
def upgrade():
    op.add_column('training_forms', 
                  sa.Column('new_field', sa.String(255), nullable=True))

def downgrade():
    op.drop_column('training_forms', 'new_field')
```

### Data Migration
- **Seed Data**: Initial admin users and training catalog
- **Data Transformation**: Convert existing data to new formats
- **Validation**: Ensure data integrity after migration

## Security Considerations

### Data Protection
- **Sensitive Data**: No passwords stored in database
- **User Privacy**: Personal data handled according to privacy policies
- **Access Control**: Database access restricted to application
- **Audit Trail**: Track changes to critical data

### SQL Injection Prevention
- **ORM Usage**: All queries through SQLAlchemy ORM
- **Parameterized Queries**: No string concatenation for queries
- **Input Validation**: All user input validated before database operations 
# Database Schema Documentation

## Overview

The Flask Survey Form System uses SQLAlchemy ORM for database operations with support for both SQLite (development) and MariaDB (production). The enhanced database schema is designed to handle comprehensive training form submissions, individual trainee management, detailed travel and material expense tracking, file attachments, user administration, and training catalog management with full relationship support.

## Database Configuration

### Development Environment
- **Database Type**: SQLite
- **File Location**: `training_forms.db`
- **Connection**: Local file-based database
- **Advantages**: Easy setup, no server required, portable, full relationship support

### Production Environment
- **Database Type**: MariaDB/MySQL
- **Server**: `azulimpbi01`
- **Port**: `3306`
- **Database Name**: `analysis`
- **Connection**: Network-based database server
- **Advantages**: Multi-user support, better performance, comprehensive backup capabilities, advanced relationship management

## Database Models

### 1. TrainingForm (training_forms)

**Purpose**: Core entity storing comprehensive training submission data with enhanced fields

**Table Structure**:
```sql
CREATE TABLE training_forms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    training_type VARCHAR NOT NULL,
    training_name VARCHAR NOT NULL,
    trainer_name VARCHAR,
    trainer_email VARCHAR,
    supplier_name VARCHAR,
    location_type VARCHAR NOT NULL,
    location_details VARCHAR,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    training_hours FLOAT,
    submission_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved BOOLEAN DEFAULT FALSE,
    concur_claim VARCHAR,
    course_cost FLOAT DEFAULT 0,
    invoice_number VARCHAR,
    training_description TEXT NOT NULL,
    submitter VARCHAR,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ida_class VARCHAR,
    deleted BOOLEAN DEFAULT FALSE NOT NULL,
    deleted_datetimestamp DATETIME
);
```

**Enhanced Field Descriptions**:
- `id`: Primary key, auto-incrementing unique identifier
- `training_type`: Type of training ("Internal Training" or "External Training")
- `training_name`: **NEW**: Name/title of the training course (required for all trainings)
- `trainer_name`: Name of trainer (required for internal training)
- `trainer_email`: **NEW**: Email of trainer (automatically captured for internal training)
- `supplier_name`: Training supplier (required for external training)
- `location_type`: Training location ("Onsite", "Offsite", or "Virtual")
- `location_details`: Specific location details (required for offsite)
- `start_date`: Training start date
- `end_date`: Training end date
- `training_hours`: Duration in hours (required for all trainings)
- `submission_date`: When the form was submitted
- `approved`: Admin approval status
- `concur_claim`: Concur expense claim number (optional)
- `course_cost`: Course fee (required for external training)
- `invoice_number`: **NEW**: Invoice number (required for external training)
- `training_description`: Detailed training description
- `submitter`: Email of the person who submitted the form
- `created_at`: Record creation timestamp
- `ida_class`: Training classification (Class A-D, required)
- `deleted`: **NEW**: Soft delete flag (boolean, default=False, not null)
- `deleted_datetimestamp`: **NEW**: Timestamp when form was deleted (datetime, nullable)

**Enhanced Business Rules**:
- **Training name is always required** for all training types
- Internal training requires `trainer_name`, `trainer_email` (auto-captured), and `training_hours`
- External training requires `supplier_name`, `course_cost`, `invoice_number`, and `training_hours`
- Offsite training requires `location_details`
- Virtual training requires attachments
- IDA class classification is mandatory for all trainings

**Relationships**:
- One-to-Many with Trainee (one form can have multiple trainees)
- One-to-Many with TravelExpense (one form can have multiple travel expenses)
- One-to-Many with MaterialExpense (one form can have multiple material expenses)
- One-to-Many with Attachment (one form can have multiple attachments)

### 2. Trainee (trainees)

**Purpose**: **NEW TABLE** - Stores individual trainee information for each training form with comprehensive details

**Table Structure**:
```sql
CREATE TABLE trainees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_id INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    department VARCHAR NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE
);
```

**Field Descriptions**:
- `id`: Primary key, auto-incrementing unique identifier
- `form_id`: Foreign key reference to training_forms.id
- `name`: Full name of the trainee
- `email`: Email address of the trainee (unique identifier)
- `department`: Department the trainee belongs to
- `created_at`: Record creation timestamp

**Business Rules**:
- Each trainee record is linked to a specific training form
- Email serves as the unique identifier for each trainee
- Department information is captured for reporting and analytics
- At least one trainee must be associated with each training form

**Relationships**:
- Many-to-One with TrainingForm (multiple trainees can belong to one form)
- Cascade delete (trainees deleted when parent form is deleted)

### 3. TravelExpense (travel_expenses)

**Purpose**: **NEW TABLE** - Stores detailed travel expense records for training-related travel with comprehensive tracking

**Table Structure**:
```sql
CREATE TABLE travel_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_id INTEGER NOT NULL,
    travel_date DATE NOT NULL,
    destination VARCHAR NOT NULL,
    traveler_type VARCHAR NOT NULL,
    traveler_email VARCHAR NOT NULL,
    traveler_name VARCHAR NOT NULL,
    travel_mode VARCHAR NOT NULL,
    cost FLOAT,
    distance_km FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE
);
```

**Field Descriptions**:
- `id`: Primary key, auto-incrementing unique identifier
- `form_id`: Foreign key reference to training_forms.id
- `travel_date`: Date of travel (must be within training period)
- `destination`: Travel destination location
- `traveler_type`: Type of traveler ("trainer" or "trainee")
- `traveler_email`: Email address of the traveler
- `traveler_name`: Name of the traveler
- `travel_mode`: Mode of transportation ("mileage", "rail", "economy_flight")
- `cost`: Travel cost (for rail and flight expenses)
- `distance_km`: Distance in kilometers (for mileage expenses)
- `created_at`: Record creation timestamp

**Enhanced Business Rules**:
- Travel date must be within a week of training start and end dates (inclusive)
- For mileage travel mode: `distance_km` is required, `cost` is calculated automatically
- For rail/flight travel modes: `cost` is required, `distance_km` is not used
- Traveler must be either the trainer or one of the trainees from the form
- Multiple travel expenses can be associated with a single training form

**Relationships**:
- Many-to-One with TrainingForm (one form can have multiple travel expenses)
- Cascade delete (travel expenses deleted when form is deleted)

### 4. MaterialExpense (material_expenses)

**Purpose**: **NEW TABLE** - Stores material expenses related to training delivery with comprehensive tracking

**Table Structure**:
```sql
CREATE TABLE material_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_id INTEGER NOT NULL,
    purchase_date DATE NOT NULL,
    supplier_name VARCHAR NOT NULL,
    invoice_number VARCHAR NOT NULL,
    material_cost FLOAT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE
);
```

**Field Descriptions**:
- `id`: Primary key, auto-incrementing unique identifier
- `form_id`: Foreign key reference to training_forms.id
- `purchase_date`: Date when materials were purchased
- `supplier_name`: Name of the supplier/vendor
- `invoice_number`: Invoice number for the purchase
- `material_cost`: Cost of the materials (required)
- `created_at`: Record creation timestamp

**Business Rules**:
- All fields are required for material expense records
- Multiple material expenses can be associated with a single training form
- Purchase date tracking for audit and reporting purposes
- Invoice number tracking for financial reconciliation

**Relationships**:
- Many-to-One with TrainingForm (one form can have multiple material expenses)
- Cascade delete (material expenses deleted when form is deleted)

### 5. Attachment (attachments)

**Purpose**: Stores metadata for file attachments linked to training forms with enhanced organization

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

**Enhanced Field Descriptions**:
- `id`: Primary key, auto-incrementing unique identifier
- `form_id`: Foreign key reference to training_forms.id
- `filename`: Secure filename with timestamp prefix (organized by form)
- `description`: Optional description of the attachment

**Enhanced Features**:
- Files are organized in form-specific directories (`uploads/form_ID/`)
- Filename includes timestamp for uniqueness and organization
- Support for multiple file descriptions
- Enhanced metadata tracking through model methods

**Relationships**:
- Many-to-One with TrainingForm (one form can have multiple attachments)
- Cascade delete (attachments deleted when form is deleted)

### 6. Admin (admins)

**Purpose**: Stores administrative user information for role-based access control

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
- Email must be unique across all admin users
- Used for role-based access control throughout the application
- Integrated with LDAP authentication for seamless login

### 7. TrainingCatalog (training_catalog)

**Purpose**: Enhanced predefined training courses for autocomplete, standardization, and quick form population

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
    course_cost FLOAT DEFAULT 0
);
```

**Enhanced Field Descriptions**:
- `id`: Primary key, auto-incrementing unique identifier
- `area`: Training area or department category
- `training_name`: Name of the training course (searchable)
- `qty_staff_attending`: Expected number of attendees
- `training_desc`: Detailed training description
- `challenge_lvl`: Difficulty level of the training
- `skill_impact`: Expected skill improvement impact
- `evaluation_method`: How training effectiveness is measured
- `ida_class`: Training classification (Class A-D)
- `training_type`: Internal or External training designation
- `training_hours`: Standard duration in hours
- `supplier_name`: Training provider name
- `course_cost`: Standard cost for the training

**Enhanced Features**:
- Searchable training catalog for quick form population
- Integrated with form submission for automatic field population
- Comprehensive metadata for training selection and reporting

## Enhanced Database Relationships

### Entity Relationship Diagram

```
TrainingForm (1) ←→ (Many) Trainee
TrainingForm (1) ←→ (Many) TravelExpense
TrainingForm (1) ←→ (Many) MaterialExpense
TrainingForm (1) ←→ (Many) Attachment
     ↓
   Submitter (User via LDAP)
     ↓
   Admin (Role-based access)

TrainingCatalog (Lookup data for forms)
```

### Enhanced Relationship Details

1. **TrainingForm ↔ Trainee** (One-to-Many)
   - **NEW RELATIONSHIP**: One training form can have multiple individual trainees
   - Each trainee has name, email, and department information
   - Trainees are deleted when the parent form is deleted (CASCADE)
   - Foreign key: `trainees.form_id → training_forms.id`
   - Minimum one trainee required per form

2. **TrainingForm ↔ TravelExpense** (One-to-Many)
   - **NEW RELATIONSHIP**: One training form can have multiple travel expense records
   - Detailed travel tracking with dates, destinations, and costs
   - Travel expenses are deleted when the parent form is deleted (CASCADE)
   - Foreign key: `travel_expenses.form_id → training_forms.id`
   - Supports multiple travelers and travel modes

3. **TrainingForm ↔ MaterialExpense** (One-to-Many)
   - **NEW RELATIONSHIP**: One training form can have multiple material expense records
   - Comprehensive material cost tracking with suppliers and invoices
   - Material expenses are deleted when the parent form is deleted (CASCADE)
   - Foreign key: `material_expenses.form_id → training_forms.id`
   - Full audit trail for material purchases

4. **TrainingForm ↔ Attachment** (One-to-Many)
   - **ENHANCED**: One training form can have multiple attachments with descriptions
   - Form-specific file organization in dedicated directories
   - Attachments are deleted when the parent form is deleted (CASCADE)
   - Foreign key: `attachments.form_id → training_forms.id`
   - Enhanced metadata and organization

5. **User ↔ TrainingForm** (One-to-Many via submitter field)
   - One user can submit multiple training forms
   - User identification through email address
   - Enhanced user tracking and form ownership
   - No direct foreign key (users managed via LDAP)

6. **Admin ↔ User** (Role assignment)
   - Admin table defines which users have administrative privileges
   - Used for authorization checks throughout the application
   - Enhanced role-based access control

## Enhanced Database Operations

### Core CRUD Operations

#### Enhanced Create Operations
```python
# Insert new training form with comprehensive related data
def insert_training_form(form_data):
    with db_session() as session:
        form = TrainingForm(**form_data)
        session.add(form)
        session.flush()
        return form.id

# Add multiple trainees for a form with full details
def insert_trainees(form_id, trainees_data):
    with db_session() as session:
        for trainee_data in trainees_data:
            trainee = Trainee(
                form_id=form_id,
                name=trainee_data["name"],
                email=trainee_data["email"],
                department=trainee_data["department"]
            )
            session.add(trainee)
        return True

# Insert comprehensive travel expenses for a form
def insert_travel_expenses(form_id, travel_expenses_data):
    with db_session() as session:
        for expense_data in travel_expenses_data:
            expense = TravelExpense(
                form_id=form_id,
                travel_date=parse_date(expense_data["travel_date"]),
                destination=expense_data["destination"],
                traveler_type=expense_data["traveler_type"],
                traveler_email=expense_data["traveler_email"],
                traveler_name=expense_data["traveler_name"],
                travel_mode=expense_data["travel_mode"],
                cost=expense_data.get("cost"),
                distance_km=expense_data.get("distance_km"),
            )
            session.add(expense)
        return True

# Insert detailed material expenses for a form
def insert_material_expenses(form_id, material_expenses_data):
    with db_session() as session:
        for expense_data in material_expenses_data:
            expense = MaterialExpense(
                form_id=form_id,
                purchase_date=parse_date(expense_data["purchase_date"]),
                supplier_name=expense_data["supplier_name"],
                invoice_number=expense_data["invoice_number"],
                material_cost=expense_data["material_cost"]
            )
            session.add(expense)
        return True
```

#### Enhanced Read Operations
```python
# Get comprehensive training form by ID with all related data
def get_training_form(form_id):
    with db_session() as session:
        form = session.query(TrainingForm).filter_by(id=form_id).first()
        if form:
            return form.to_dict(include_costs=True)
        return None

# Get all forms with enhanced filtering and search capabilities
def get_all_training_forms(search_term="", date_from=None, date_to=None, 
                          training_type=None, approval_status=None,
                          sort_by="submission_date", sort_order="DESC", page=1):
    # Enhanced query with new field searches and relationship traversal
    with db_session() as session:
        query = session.query(TrainingForm)
        
        # Enhanced search including new fields
        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.filter(
                or_(
                    TrainingForm.training_name.contains(search_term),
                    TrainingForm.training_description.contains(search_term),
                    TrainingForm.trainer_name.contains(search_term),
                    TrainingForm.trainer_email.contains(search_term),
                    TrainingForm.supplier_name.contains(search_term)
                )
            )
        
        # Apply additional filters and pagination
        return _apply_sorting_and_pagination(query, sort_by, sort_order, page)

# Get comprehensive trainee list for a form
def get_trainees(form_id):
    with db_session() as session:
        trainees = session.query(Trainee).filter_by(form_id=form_id).all()
        return [trainee.to_dict() for trainee in trainees]

# Get detailed travel expenses for a form
def get_travel_expenses(form_id):
    with db_session() as session:
        expenses = session.query(TravelExpense).filter_by(form_id=form_id).all()
        return [expense.to_dict() for expense in expenses]

# Get comprehensive material expenses for a form
def get_material_expenses(form_id):
    with db_session() as session:
        expenses = session.query(MaterialExpense).filter_by(form_id=form_id).all()
        return [expense.to_dict() for expense in expenses]
```

#### Enhanced Update Operations
```python
# Update training form with new fields
def update_training_form(form_id, form_data):
    with db_session() as session:
        form = session.query(TrainingForm).filter_by(id=form_id).first()
        if form:
            form.update_from_dict(form_data)
            return True
        return False

# Update trainees for a form (replace all with new data)
def update_trainees(form_id, trainees_data):
    with db_session() as session:
        # Delete existing trainees
        session.query(Trainee).filter_by(form_id=form_id).delete()
        # Insert new trainees
        for trainee_data in trainees_data:
            trainee = Trainee(form_id=form_id, **trainee_data)
            session.add(trainee)
        return True

# Update travel expenses for a form
def update_travel_expenses(form_id, travel_expenses_data):
    with db_session() as session:
        # Delete existing travel expenses
        session.query(TravelExpense).filter_by(form_id=form_id).delete()
        # Insert new travel expenses
        for expense_data in travel_expenses_data:
            expense = TravelExpense(form_id=form_id, **expense_data)
            session.add(expense)
        return True

# Update material expenses for a form
def update_material_expenses(form_id, material_expenses_data):
    with db_session() as session:
        # Delete existing material expenses
        session.query(MaterialExpense).filter_by(form_id=form_id).delete()
        # Insert new material expenses
        for expense_data in material_expenses_data:
            expense = MaterialExpense(form_id=form_id, **expense_data)
            session.add(expense)
        return True
```

#### Enhanced Delete Operations
```python
# Enhanced soft delete functionality (no physical deletion)
def soft_delete_training_form(form_id):
    """Mark a training form as deleted with timestamp (soft delete)"""
    with db_session() as session:
        form = session.query(TrainingForm).filter_by(id=form_id).first()
        if form:
            form.deleted = True
            form.deleted_datetimestamp = datetime.now()
            return True
        return False

def recover_training_form(form_id):
    """Recover a soft-deleted training form"""
    with db_session() as session:
        form = session.query(TrainingForm).filter_by(id=form_id).first()
        if form and form.deleted:
            form.deleted = False
            form.deleted_datetimestamp = None
            return True
        return False

# Enhanced read operations with delete status filtering
def get_training_form(form_id, include_deleted=False):
    """Get training form by ID with optional inclusion of deleted forms"""
    with db_session() as session:
        query = session.query(TrainingForm).filter_by(id=form_id)
        if not include_deleted:
            query = query.filter_by(deleted=False)
        form = query.first()
        if form:
            return form.to_dict(include_costs=True)
        return None

def get_all_training_forms(search_term="", date_from=None, date_to=None, 
                          training_type=None, approval_status=None, delete_status="",
                          sort_by="submission_date", sort_order="DESC", page=1):
    """Enhanced query with delete status filtering"""
    with db_session() as session:
        query = session.query(TrainingForm)
        
        # Apply delete status filter
        query = _apply_training_form_filters(query, search_term, date_from, date_to,
                                           training_type, approval_status, delete_status)
        
        return _apply_sorting_and_pagination(query, sort_by, sort_order, page)

# Note: Physical deletion is not implemented in current version
# Forms are retained for 180 days before permanent deletion (future implementation)
```

### Advanced Query Operations

#### Enhanced Search and Filter
```python
# Multi-criteria search including all new fields and relationships with delete status
def _apply_training_form_filters(query, search_term="", date_from=None, 
                                date_to=None, training_type=None, approval_status=None, 
                                delete_status=""):
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            or_(
                TrainingForm.training_name.contains(search_term),
                TrainingForm.training_description.contains(search_term),
                TrainingForm.trainer_name.contains(search_term),
                TrainingForm.trainer_email.contains(search_term),
                TrainingForm.supplier_name.contains(search_term),
                TrainingForm.invoice_number.contains(search_term)
            )
        )

    if date_from:
        query = query.filter(TrainingForm.start_date >= date_from)

    if date_to:
        query = query.filter(TrainingForm.end_date <= date_to)

    if training_type:
        query = query.filter(TrainingForm.training_type == training_type)
    
    if approval_status == "approved":
        query = query.filter(TrainingForm.approved == True)
    elif approval_status == "unapproved":
        query = query.filter(TrainingForm.approved == False)

    # Enhanced delete status filtering
    if delete_status == "deleted":
        query = query.filter(TrainingForm.deleted == True)
    elif delete_status == "all":
        # No filter - show all forms regardless of delete status
        pass
    else:  # Default behavior - show only non-deleted forms
        query = query.filter(TrainingForm.deleted == False)

    return query
```

#### Enhanced Pagination with Relationships
```python
# Efficient pagination for large datasets with relationship data
def _apply_sorting_and_pagination(query, sort_by="submission_date", sort_order="DESC", 
                                 page=1, page_size=10):
    # Apply sorting with new fields
    sort_field = getattr(TrainingForm, sort_by, TrainingForm.submission_date)
    if sort_order.upper() == "ASC":
        query = query.order_by(sort_field.asc())
    else:
        query = query.order_by(sort_field.desc())
    
    # Apply pagination
    offset = (page - 1) * page_size
    forms = query.offset(offset).limit(page_size).all()
    total_count = query.count()
    
    # Return enhanced data with relationships
    result = []
    for form in forms:
        form_dict = form.to_dict()
        form_dict['trainee_count'] = len(form.trainees)
        form_dict['attachment_count'] = len(form.attachments)
        result.append(form_dict)
    
    return result, total_count
```

#### Enhanced Aggregation Queries
```python
# Comprehensive training statistics for leaderboard and analytics
def get_training_statistics():
    with db_session() as session:
        # Basic statistics
        stats = session.query(
            TrainingForm.submitter,
            func.count(TrainingForm.id).label('total_submissions'),
            func.sum(TrainingForm.training_hours).label('total_hours'),
            func.sum(TrainingForm.course_cost).label('total_course_cost')
        ).group_by(TrainingForm.submitter).all()
        
        # Enhanced statistics with relationships
        result = []
        for stat in stats:
            # Get trainee count for this submitter
            trainee_count = session.query(func.count(Trainee.id)).join(TrainingForm).filter(
                TrainingForm.submitter == stat.submitter
            ).scalar()
            
            result.append({
                'submitter': stat.submitter,
                'total_submissions': stat.total_submissions,
                'total_hours': float(stat.total_hours or 0),
                'total_cost': float(stat.total_course_cost or 0),
                'total_trainees': trainee_count
            })
        
        return result

# Department-wise training statistics
def get_department_statistics():
    with db_session() as session:
        stats = session.query(
            Trainee.department,
            func.count(Trainee.id).label('trainee_count'),
            func.count(TrainingForm.id.distinct()).label('training_count')
        ).join(TrainingForm).group_by(Trainee.department).all()
        
        return [
            {
                'department': stat.department,
                'trainee_count': stat.trainee_count,
                'training_count': stat.training_count
            }
            for stat in stats
        ]
```

## Enhanced Data Validation and Constraints

### Database-Level Constraints
- **NOT NULL**: Required fields enforced at database level for data integrity
- **DEFAULT VALUES**: Automatic default values for optional fields
- **FOREIGN KEY**: Referential integrity for all relationships
- **CASCADE DELETE**: Automatic cleanup of related records

### Enhanced Application-Level Validation
- **Form Validation**: WTForms validators with conditional logic for user input
- **Business Rules**: Custom validation logic in form classes with training type awareness
- **Data Type Validation**: Automatic type conversion and validation
- **File Validation**: Enhanced file type, size, and organization constraints
- **Relationship Validation**: Ensure traveler emails match trainees or trainer

## Enhanced Performance Considerations

### Comprehensive Indexing Strategy
```sql
-- Recommended indexes for optimal performance
CREATE INDEX idx_training_forms_submitter ON training_forms(submitter);
CREATE INDEX idx_training_forms_submission_date ON training_forms(submission_date);
CREATE INDEX idx_training_forms_start_date ON training_forms(start_date);
CREATE INDEX idx_training_forms_approved ON training_forms(approved);
CREATE INDEX idx_training_forms_training_name ON training_forms(training_name);
CREATE INDEX idx_training_forms_training_type ON training_forms(training_type);
CREATE INDEX idx_training_forms_trainer_email ON training_forms(trainer_email);

-- Indexes for related tables
CREATE INDEX idx_trainees_form_id ON trainees(form_id);
CREATE INDEX idx_trainees_email ON trainees(email);
CREATE INDEX idx_trainees_department ON trainees(department);
CREATE INDEX idx_attachments_form_id ON attachments(form_id);
CREATE INDEX idx_travel_expenses_form_id ON travel_expenses(form_id);
CREATE INDEX idx_travel_expenses_travel_date ON travel_expenses(travel_date);
CREATE INDEX idx_travel_expenses_traveler_email ON travel_expenses(traveler_email);
CREATE INDEX idx_material_expenses_form_id ON material_expenses(form_id);
CREATE INDEX idx_material_expenses_purchase_date ON material_expenses(purchase_date);

-- Training catalog indexes
CREATE INDEX idx_training_catalog_training_name ON training_catalog(training_name);
CREATE INDEX idx_training_catalog_area ON training_catalog(area);
CREATE INDEX idx_training_catalog_training_type ON training_catalog(training_type);
```

### Enhanced Query Optimization
- **Pagination**: Limit result sets to manageable sizes with relationship data
- **Selective Loading**: Only load required fields for list views
- **Eager Loading**: Load related data in single queries when needed for detail views
- **Connection Pooling**: Reuse database connections efficiently
- **Relationship Optimization**: Efficient loading of related trainee, expense, and attachment data

### Enhanced Caching Strategy
- **Lookup Data**: Cache training catalog and employee data
- **Session Data**: Cache user session information
- **Query Results**: Cache frequently accessed data with invalidation
- **Relationship Data**: Cache trainee and expense data for active forms

## Enhanced Backup and Recovery

### Development Environment
- **SQLite File Backup**: Simple file copy for backup with all relationships
- **Version Control**: Database schema tracked in git
- **Migration Scripts**: Database changes managed through migrations
- **Data Export**: Enhanced export capabilities for all related data

### Production Environment
- **Automated Backups**: Regular database dumps with relationship integrity
- **Point-in-Time Recovery**: Transaction log backups
- **Disaster Recovery**: Off-site backup storage
- **Data Retention**: Configurable retention policies for all tables

## Enhanced Migration Management

### Schema Changes
```python
# Example migration for adding new relationships
def upgrade():
    op.create_table('trainees',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('form_id', sa.Integer(), sa.ForeignKey('training_forms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('department', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

def downgrade():
    op.drop_table('trainees')
```

### Enhanced Data Migration
- **Seed Data**: Initial admin users and comprehensive training catalog
- **Data Transformation**: Convert existing data to new formats with relationships
- **Validation**: Ensure data integrity after migration with relationship checks
- **Relationship Migration**: Migrate existing form data to new relationship structure

## Enhanced Security Considerations

### Data Protection
- **Sensitive Data**: No passwords stored in database
- **User Privacy**: Personal data handled according to privacy policies with consent
- **Access Control**: Database access restricted to application with role-based permissions
- **Audit Trail**: Track changes to critical data with comprehensive logging

### SQL Injection Prevention
- **ORM Usage**: All queries through SQLAlchemy ORM with parameterized statements
- **Parameterized Queries**: No string concatenation for queries
- **Input Validation**: All user input validated before database operations with business logic

### Enhanced Data Integrity
- **Foreign Key Constraints**: Ensure referential integrity across all relationships
- **Transaction Management**: Atomic operations for complex form submissions
- **Cascade Rules**: Proper cleanup of related data when parent records are deleted
- **Data Validation**: Comprehensive validation at database and application levels

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
CREATE INDEX idx_training_forms_training_name ON training_forms(training_name);
CREATE INDEX idx_trainees_form_id ON trainees(form_id);
CREATE INDEX idx_trainees_email ON trainees(email);
CREATE INDEX idx_attachments_form_id ON attachments(form_id);
CREATE INDEX idx_travel_expenses_form_id ON travel_expenses(form_id);
CREATE INDEX idx_travel_expenses_travel_date ON travel_expenses(travel_date);
CREATE INDEX idx_travel_expenses_traveler_email ON travel_expenses(traveler_email);
CREATE INDEX idx_material_expenses_form_id ON material_expenses(form_id);
CREATE INDEX idx_material_expenses_purchase_date ON material_expenses(purchase_date);
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
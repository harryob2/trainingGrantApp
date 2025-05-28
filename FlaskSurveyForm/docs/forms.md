# Form System Documentation

## Overview

The Flask Survey Form System uses WTForms for form handling, validation, and rendering. The form system implements dynamic validation based on training type, comprehensive field validation, and secure file upload handling.

## Form Architecture

### Core Components

1. **TrainingForm** (`forms.py`): Main training submission form
2. **SearchForm** (`forms.py`): Search and filtering interface
3. **LoginForm** (`forms.py`): User authentication form
4. **InvoiceForm** (`forms.py`): Invoice attachment handling
5. **Dynamic Validation** (`forms.py`): Context-aware validation logic
6. **File Upload** (`forms.py`, `utils.py`): Secure file handling

### Form Processing Flow

```
Form Display → User Input → Client Validation → Server Validation → Data Processing → Database Storage
```

## TrainingForm - Main Form

### Form Structure

```python
class TrainingForm(FlaskForm):
    # Always Required Fields
    training_type = RadioField("Training Type", choices=[...], validators=[DataRequired()])
    location_type = RadioField("Location", choices=[...], validators=[DataRequired()])
    start_date = DateField("Start Date", validators=[DataRequired()])
    end_date = DateField("End Date", validators=[DataRequired()])
    training_description = TextAreaField("Training Description", validators=[DataRequired()])
    ida_class = SelectField("Training Class", choices=[...], validators=[DataRequired()])
    
    # Conditionally Required Fields
    trainer_name = StringField("Trainer Name", validators=[DynamicRequiredIf("training_type", "Internal Training")])
    supplier_name = StringField("Supplier Name", validators=[DynamicRequiredIf("training_type", "External Training")])
    location_details = StringField("Location Details", validators=[DynamicRequiredIf("location_type", "Offsite")])
    training_hours = FloatField("Training Hours", validators=[DynamicRequiredIf("training_type", "Internal Training")])
    course_cost = FloatField("Course Cost", validators=[DynamicRequiredIf("training_type", "External Training")])
    
    # Optional Fields
    travel_cost = FloatField("Travel Expenses", validators=[Optional(), NumberRange(min=0)])
    food_cost = FloatField("Food & Accommodation", validators=[Optional(), NumberRange(min=0)])
    materials_cost = FloatField("Materials", validators=[Optional(), NumberRange(min=0)])
    other_cost = FloatField("Other Expenses", validators=[Optional(), NumberRange(min=0)])
    other_expense_description = TextAreaField("Other Expense Description", validators=[Optional()])
    concur_claim = StringField("Concur Claim Number", validators=[Optional()])
    
    # File Upload
    attachments = MultipleFileField("Attachments", validators=[DynamicRequiredIf("location_type", "Virtual")])
    attachment_descriptions = TextAreaField("Attachment Descriptions", validators=[Optional()])
    
    # Trainee Information
    trainee_emails = TextAreaField("Trainee Emails", validators=[Optional()])
    
    # Hidden Fields
    department = HiddenField("Department", default="Engineering")
    trainees_data = HiddenField("Trainees Data")
```

### Field Categories

#### Always Required Fields
- **training_type**: Internal or External training
- **location_type**: Onsite, Offsite, or Virtual
- **start_date**: Training start date
- **end_date**: Training end date
- **training_description**: Detailed description of training
- **ida_class**: Training classification (Class A-D)

#### Conditionally Required Fields
- **trainer_name**: Required for Internal Training
- **supplier_name**: Required for External Training
- **location_details**: Required for Offsite training
- **training_hours**: Required for Internal Training
- **course_cost**: Required for External Training
- **attachments**: Required for Virtual training

#### Optional Fields
- **travel_cost**: Travel expenses
- **food_cost**: Food and accommodation costs
- **materials_cost**: Training materials cost
- **other_cost**: Other miscellaneous expenses
- **other_expense_description**: Description of other expenses
- **concur_claim**: Concur expense claim number
- **trainee_emails**: Comma/space separated trainee emails

## Dynamic Validation System

### DynamicRequiredIf Validator

The system implements a custom validator that makes fields required based on other field values:

```python
def DynamicRequiredIf(condition_field, condition_value, additional_validator=None):
    """Dynamic required validator based on a condition"""
    
    def _validator(form, field):
        try:
            other_field = getattr(form, condition_field)
        except AttributeError:
            raise ValidationError(f"No field named '{condition_field}' in form for RequiredIf validator.")
        
        if other_field.data == condition_value:
            # If condition is met, field is required
            validators = [DataRequired()] if not additional_validator else [DataRequired(), additional_validator]
            field.validators = validators
        else:
            # Make it optional if condition is not met
            field.validators = [Optional()] if not additional_validator else [Optional(), additional_validator]
    
    return _validator
```

### Validation Rules

#### Training Type Dependencies
```python
# Internal Training Requirements
trainer_name = StringField("Trainer Name", 
    validators=[DynamicRequiredIf("training_type", "Internal Training")])
training_hours = FloatField("Training Hours", 
    validators=[DynamicRequiredIf("training_type", "Internal Training", 
                NumberRange(min=0, message="Training Hours cannot be negative."))])

# External Training Requirements
supplier_name = StringField("Supplier Name", 
    validators=[DynamicRequiredIf("training_type", "External Training")])
course_cost = FloatField("Course Cost", 
    validators=[DynamicRequiredIf("training_type", "External Training", 
                NumberRange(min=0, message="Course Cost cannot be negative."))])
```

#### Location Type Dependencies
```python
# Offsite Training Requirements
location_details = StringField("Location Details", 
    validators=[DynamicRequiredIf("location_type", "Offsite")])

# Virtual Training Requirements
attachments = MultipleFileField("Attachments", 
    validators=[DynamicRequiredIf("location_type", "Virtual")])
```

## Custom Validation Methods

### Date Validation
```python
def validate_end_date(self, field):
    """Ensure end date is not before start date"""
    if field.data and self.start_date.data:
        if field.data < self.start_date.data:
            raise ValidationError("End date cannot be before start date.")
```

### Concur Claim Validation
```python
def validate_concur_claim(self, field):
    """Validate Concur claim number format"""
    if field.data:
        # Remove spaces and check if it's alphanumeric
        claim_clean = field.data.replace(" ", "")
        if not claim_clean.isalnum():
            raise ValidationError("Concur claim number should contain only letters and numbers.")
        if len(claim_clean) < 3:
            raise ValidationError("Concur claim number seems too short.")
```

### Expense Description Validation
```python
def validate_other_expense_description(self, field):
    """Require description when other expenses are entered"""
    if self.other_cost.data and self.other_cost.data > 0:
        if not field.data or not field.data.strip():
            raise ValidationError("Description is required when other expenses are entered.")
```

### File Upload Validation
```python
def validate_attachments(self, field):
    """Validate file uploads for virtual training"""
    if self.location_type.data == "Virtual":
        if not field.data or not any(f.filename for f in field.data if f):
            raise ValidationError("At least one attachment is required for virtual training.")
```

### Trainee Data Validation
```python
def validate_trainees_data(self, field):
    """Validate trainee data JSON"""
    if field.data:
        try:
            trainees = json.loads(field.data)
            if not isinstance(trainees, list):
                raise ValidationError("Invalid trainee data format.")
        except json.JSONDecodeError:
            raise ValidationError("Invalid trainee data format.")
```

## Form Data Processing

### Email Processing
```python
def process_emails(self):
    """Process comma/space separated emails into a list"""
    if not self.trainee_emails.data:
        return []
    
    # Split by comma or space and clean up
    emails = re.split(r'[,\s]+', self.trainee_emails.data.strip())
    return [email.strip() for email in emails if email.strip()]
```

### Form Data Preparation
```python
def prepare_form_data(self):
    """Prepare form data for database storage"""
    # Process trainee emails
    trainee_emails = self.process_emails()
    
    # Create trainee data structure
    trainees_data = []
    for email in trainee_emails:
        if email:  # Skip empty emails
            trainees_data.append({
                "email": email,
                "name": email.split("@")[0].replace(".", " ").title()  # Basic name extraction
            })
    
    # Prepare form data dictionary
    data = {
        "training_type": self.training_type.data,
        "trainer_name": self.trainer_name.data if self.training_type.data == "Internal Training" else None,
        "supplier_name": self.supplier_name.data if self.training_type.data == "External Training" else None,
        "location_type": self.location_type.data,
        "location_details": self.location_details.data if self.location_type.data == "Offsite" else None,
        "start_date": self.start_date.data,
        "end_date": self.end_date.data,
        "training_hours": self.training_hours.data if self.training_type.data == "Internal Training" else None,
        "trainees_data": json.dumps(trainees_data),
        "training_description": self.training_description.data,
        "ida_class": self.ida_class.data,
        "travel_cost": self.travel_cost.data or 0,
        "food_cost": self.food_cost.data or 0,
        "materials_cost": self.materials_cost.data or 0,
        "other_cost": self.other_cost.data or 0,
        "other_expense_description": self.other_expense_description.data,
        "course_cost": self.course_cost.data if self.training_type.data == "External Training" else 0,
        "concur_claim": self.concur_claim.data,
        "submitter": current_user.email,
        "department": self.department.data
    }
    
    return data
```

## File Upload System

### Allowed File Types
```python
ALLOWED_EXTENSIONS = {
    "pdf", "doc", "docx", "xls", "xlsx", 
    "jpg", "jpeg", "png", "csv", "txt"
}
```

### File Validation
```python
def allowed_file(filename):
    """Check if a filename has an allowed extension"""
    return (filename and "." in filename and 
            filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS)
```

### Secure File Saving
```python
def save_file(file):
    """Save an uploaded file with a unique filename"""
    if not file or not file.filename or not allowed_file(file.filename):
        return None
    
    try:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        file.save(file_path)
        return unique_filename
    except Exception as e:
        logging.error(f"Error saving file: {e}")
        return None
```

### File Upload Processing
```python
# In form submission handler
uploaded_files = []
if form.attachments.data:
    for file in form.attachments.data:
        if file and file.filename:
            filename = save_file(file)
            if filename:
                uploaded_files.append(filename)

# Save attachment metadata to database
for i, filename in enumerate(uploaded_files):
    description = attachment_descriptions[i] if i < len(attachment_descriptions) else ""
    attachment = Attachment(
        form_id=form_id,
        filename=filename,
        description=description
    )
    session.add(attachment)
```

## SearchForm - Filtering Interface

### Form Structure
```python
class SearchForm(FlaskForm):
    search = StringField("Search", validators=[Optional()])
    date_from = DateField("From Date", validators=[Optional()], format="%Y-%m-%d")
    date_to = DateField("To Date", validators=[Optional()], format="%Y-%m-%d")
    training_type = SelectField("Training Type", 
        choices=[("", "All Types")] + [(type, type) for type in TRAINING_TYPES],
        validators=[Optional()])
    sort_by = SelectField("Sort By", choices=SORT_OPTIONS, default="submission_date")
    sort_order = SelectField("Order", 
        choices=[("DESC", "Newest First"), ("ASC", "Oldest First")], 
        default="DESC")
    submit = SubmitField("Search")
```

### Date Range Validation
```python
def validate_date_to(self, field):
    """Ensure 'to' date is not before 'from' date"""
    if field.data and self.date_from.data:
        if field.data < self.date_from.data:
            raise ValidationError("'To' date cannot be before 'From' date.")
```

## LoginForm - Authentication

### Form Structure
```python
class LoginForm(FlaskForm):
    username = StringField("Username (Email)", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
```

### Email Validation
- Uses WTForms Email validator
- Ensures proper email format
- Required field validation

## InvoiceForm - Invoice Attachments

### Form Structure
```python
class InvoiceForm(FlaskForm):
    invoice_number = StringField("Invoice Number", validators=[Optional()])
    cost = DecimalField("Cost (€)", validators=[DataRequired(), NumberRange(min=0)], places=2)
    description = TextAreaField("Description", validators=[Optional()])
    attachment = FileField("Invoice Attachment", 
        validators=[Optional(), FileAllowed(list(ALLOWED_EXTENSIONS), "Only document files are allowed.")])
    submit = SubmitField("Add Invoice")
```

## Form Rendering and Templates

### Template Integration

#### Form Rendering
```html
<!-- Basic field rendering -->
{{ form.training_type.label(class="form-label") }}
{{ form.training_type(class="form-control") }}
{% if form.training_type.errors %}
    <div class="invalid-feedback d-block">
        {% for error in form.training_type.errors %}
            {{ error }}
        {% endfor %}
    </div>
{% endif %}

<!-- Dynamic field rendering with conditions -->
<div id="trainer-name-group" class="mb-3" style="display: none;">
    {{ form.trainer_name.label(class="form-label") }}
    {{ form.trainer_name(class="form-control", **{"data-lookup": "employees"}) }}
    {% if form.trainer_name.errors %}
        <div class="invalid-feedback d-block">
            {% for error in form.trainer_name.errors %}
                {{ error }}
            {% endfor %}
        {% endif %}
    </div>
</div>
```

#### JavaScript Integration
```javascript
// Dynamic field visibility based on training type
document.getElementById('training_type').addEventListener('change', function() {
    const trainingType = this.value;
    const trainerGroup = document.getElementById('trainer-name-group');
    const supplierGroup = document.getElementById('supplier-name-group');
    
    if (trainingType === 'Internal Training') {
        trainerGroup.style.display = 'block';
        supplierGroup.style.display = 'none';
    } else if (trainingType === 'External Training') {
        trainerGroup.style.display = 'none';
        supplierGroup.style.display = 'block';
    }
});
```

### CSRF Protection

All forms include CSRF protection:
```html
{{ form.hidden_tag() }}  <!-- Includes CSRF token -->
```

## Form Processing Workflow

### Submission Processing
```python
@app.route("/submit", methods=["GET", "POST"])
@login_required
def submit_form():
    form = TrainingForm()
    
    if form.validate_on_submit():
        try:
            # Prepare form data
            form_data = form.prepare_form_data()
            
            # Insert into database
            form_id = insert_training_form(form_data)
            
            # Handle file uploads
            if form.attachments.data:
                handle_file_uploads(form, form_id)
            
            flash("Training form submitted successfully!", "success")
            return redirect(url_for("success"))
            
        except Exception as e:
            logging.error(f"Error submitting form: {e}")
            flash("An error occurred while submitting the form.", "danger")
    
    return render_template("index.html", form=form)
```

### Edit Processing
```python
@app.route("/edit/<int:form_id>", methods=["GET", "POST"])
@login_required
def edit_form(form_id):
    # Get existing form data
    existing_form = get_training_form(form_id)
    
    # Check permissions
    if not can_edit_form(current_user, existing_form):
        abort(403)
    
    form = TrainingForm()
    
    if request.method == "GET":
        # Populate form with existing data
        populate_form_from_data(form, existing_form)
    
    if form.validate_on_submit():
        # Update form data
        form_data = form.prepare_form_data()
        update_training_form(form_id, form_data)
        
        flash("Training form updated successfully!", "success")
        return redirect(url_for("view_form", form_id=form_id))
    
    return render_template("index.html", form=form, edit_mode=True)
```

## Error Handling

### Validation Error Display
```python
# Server-side validation errors are automatically displayed in templates
{% if form.field_name.errors %}
    <div class="invalid-feedback d-block">
        {% for error in form.field_name.errors %}
            {{ error }}
        {% endfor %}
    </div>
{% endif %}
```

### Flash Messages
```python
# Success messages
flash("Training form submitted successfully!", "success")

# Error messages
flash("Please correct the errors below.", "danger")

# Warning messages
flash("Some fields require attention.", "warning")

# Info messages
flash("Form saved as draft.", "info")
```

## Form Security

### Input Sanitization
- All form inputs are automatically escaped by Jinja2 templates
- WTForms provides built-in XSS protection
- File uploads are validated for type and size

### CSRF Protection
- All forms include CSRF tokens
- Tokens are validated on form submission
- Protection against cross-site request forgery

### File Upload Security
- File type validation using allowed extensions
- Secure filename generation using `secure_filename()`
- File size limits enforced
- Files stored outside web root

## Performance Considerations

### Form Optimization
- **Lazy Loading**: Employee and training catalog data loaded via AJAX
- **Caching**: Lookup data cached in memory
- **Validation**: Client-side validation reduces server load
- **File Handling**: Efficient file upload processing

### Database Optimization
- **Prepared Statements**: ORM uses parameterized queries
- **Transaction Management**: Atomic form submissions
- **Indexing**: Database indexes on frequently queried fields 
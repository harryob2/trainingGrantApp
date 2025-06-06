from datetime import date
import re
import json
import logging

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    SelectField,
    RadioField,
    DecimalField,
    DateField,
    SubmitField,
    TextAreaField,
    HiddenField,
    FloatField,
    MultipleFileField,
    PasswordField,
    IntegerField,
)
from wtforms.validators import (
    DataRequired,
    NumberRange,
    Optional,
    ValidationError,
    Email,
)

# Configure logging for form debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Training types
TRAINING_TYPES = ["Internal Training", "External Training"]

# IDA Class options
IDA_CLASS_CHOICES = [
    ("Class A - QQI Certified L1-10", "Class A - QQI Certified L1-10"),
    ("Class B - Nat/International Industry Cert", "Class B - Nat/International Industry Cert"),
    ("Class C - Internal Corporate Cert", "Class C - Internal Corporate Cert"),
    ("Class D - Not Certified", "Class D - Not Certified"),
    ("Training not completed/ongoing", "Training not completed/ongoing"),
    ("Not sure", "Not sure"),
]

# Sort options
SORT_OPTIONS = [
    ("submission_date", "Submission Date"),
    ("start_date", "Start Date"),
    ("end_date", "End Date"),
    ("cost", "Cost"),
]

# Approval status options
APPROVAL_STATUS_OPTIONS = [
    ("", "All Statuses"),
    ("approved", "Approved"),
    ("unapproved", "Unapproved"),
]

# Allowed file extensions for file upload
ALLOWED_EXTENSIONS = {
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "jpg",
    "jpeg",
    "png",
    "csv",
    "txt",
}


def RequiredIf(condition_field, condition_value, message=None):
    """Validator that makes field required if another field has a specific value"""
    
    def _validator(form, field):
        try:
            other_field = getattr(form, condition_field)
        except AttributeError:
            raise ValidationError(
                f"No field named '{condition_field}' in form for RequiredIf validator."
            )
        
        logger.debug(f"RequiredIf: Checking {field.name} based on {condition_field} == {condition_value}")
        logger.debug(f"RequiredIf: Other field value: {other_field.data}")
        logger.debug(f"RequiredIf: Current field value: {field.data}")
        
        # If the condition is met and the field is empty or None, it's required
        if other_field.data == condition_value:
            if not field.data or (isinstance(field.data, str) and not field.data.strip()):
                error_message = message or f"This field is required when {condition_field} is {condition_value}."
                logger.debug(f"RequiredIf: Validation failed - {error_message}")
                raise ValidationError(error_message)
            else:
                logger.debug(f"RequiredIf: Validation passed - field has value")
        else:
            logger.debug(f"RequiredIf: Condition not met, field is optional")
    
    return _validator


def RequiredIfExternal(message=None):
    """Validator that makes field required if training type is External Training"""
    return RequiredIf("training_type", "External Training", message)


class SmartFloatField(FloatField):
    """FloatField that handles empty strings gracefully by converting them to None"""
    
    def process_formdata(self, valuelist):
        if valuelist:
            # Convert empty strings to None before float conversion
            if valuelist[0] == '' or valuelist[0] is None:
                self.data = None
                return
        # Use parent's processing for non-empty values
        super().process_formdata(valuelist)


def ExternalTrainingField(message=None, min_value=0):
    """Comprehensive validator for external training fields that handles requirement and range"""
    def _validator(form, field):
        if form.training_type.data == "External Training":
            # Required for external training
            if not field.data and field.data != 0:
                raise ValidationError(message or f"This field is required for external training.")
            # Must be non-negative if provided
            if field.data is not None and field.data < min_value:
                raise ValidationError(f"Value cannot be negative.")
        # For internal training, clear the field to prevent validation issues
        elif form.training_type.data == "Internal Training":
            field.data = None
    return _validator


def RequiredIfInternal(message=None):
    """Validator that makes field required if training type is Internal Training"""
    return RequiredIf("training_type", "Internal Training", message)


def RequiredIfOffsite(message=None):
    """Validator that makes field required if location type is Offsite"""
    return RequiredIf("location_type", "Offsite", message)


def RequiredIfVirtual(message=None):
    """Validator that makes field required if location type is Virtual"""
    return RequiredIf("location_type", "Virtual", message)


def RequiredAttachmentsIfVirtual(message=None):
    """Special validator for attachments when location type is Virtual"""
    
    def _validator(form, field):
        try:
            location_field = getattr(form, "location_type")
        except AttributeError:
            raise ValidationError("No location_type field found in form.")
        
        logger.debug(f"RequiredAttachmentsIfVirtual: Checking attachments based on location_type == Virtual")
        logger.debug(f"RequiredAttachmentsIfVirtual: Location type value: {location_field.data}")
        logger.debug(f"RequiredAttachmentsIfVirtual: Attachments field data: {field.data}")
        
        # If location is Virtual, check if attachments are provided
        if location_field.data == "Virtual":
            # Check if any files were uploaded
            has_attachments = field.data and any(f.filename for f in field.data if f)
            logger.debug(f"RequiredAttachmentsIfVirtual: Has attachments: {has_attachments}")
            
            if not has_attachments:
                error_message = message or "At least one attachment is required for Virtual training."
                logger.debug(f"RequiredAttachmentsIfVirtual: Validation failed - {error_message}")
                raise ValidationError(error_message)
            else:
                logger.debug(f"RequiredAttachmentsIfVirtual: Validation passed - attachments found")
        else:
            logger.debug(f"RequiredAttachmentsIfVirtual: Location is not Virtual, attachments are optional")
    
    return _validator


class TrainingForm(FlaskForm):
    """Form for training submissions"""

    # Always Required
    training_type = RadioField(
        "Training Type",
        choices=[
            ("Internal Training", "Internal Training"),
            ("External Training", "External Training"),
        ],
        validators=[DataRequired()],
    )
    training_name = StringField(
        "Training Name",
        validators=[DataRequired(message="Training Name is required.")],
        description="The name/title of the training course",
    )
    location_type = RadioField(
        "Location",
        choices=[("Onsite", "Onsite"), ("Offsite", "Offsite"), ("Virtual", "Virtual")],
        validators=[
            DataRequired("Please select a location type.")
        ],  # Custom message example
    )
    start_date = DateField(
        "Start Date", validators=[DataRequired()], format="%Y-%m-%d", default=date.today
    )
    end_date = DateField(
        "End Date", validators=[DataRequired()], format="%Y-%m-%d", default=date.today
    )
    training_description = TextAreaField(
        "Training Description", validators=[DataRequired()]
    )
    notes = TextAreaField(
        "Notes for Reviewer", 
        validators=[Optional()],
        description="Optional notes for the person reviewing this form submission"
    )
    ida_class = SelectField(
        "Training Class",
        choices=IDA_CLASS_CHOICES,
        validators=[DataRequired()]
    )

    # Conditionally Required
    trainer_name = StringField(
        "Trainer Name",
        validators=[RequiredIfInternal("Trainer Name is required for internal training.")],
        description="For internal training, select from employee list",
    )
    supplier_name = StringField(
        "Supplier Name",
        validators=[RequiredIfExternal("Supplier Name is required for external training.")],
        description="For external training, enter supplier name",
    )
    location_details = StringField(
        "Location Details",
        validators=[RequiredIfOffsite("Location Details is required for offsite training.")],
        description="Required for offsite training",
    )
    training_hours = FloatField(
        "Training Hours",
        validators=[
            DataRequired(message="Training Hours is required."),
            NumberRange(min=0, message="Training Hours cannot be negative."),
        ],
        default=None,
        render_kw={"type": "number", "step": "0.1", "min": "0"},
    )
    course_cost = SmartFloatField(
        "Course Cost",
        validators=[
            ExternalTrainingField("Course Cost is required for external training.", min_value=0),
        ],
        default=None,
    )
    invoice_number = StringField(
        "Invoice Number",
        validators=[RequiredIfExternal("Invoice Number is required for external training.")],
        description="Invoice number for external training course",
    )
    concur_claim = StringField("Concur Claim Number", validators=[RequiredIfExternal("Concur Claim Number is required for external training.")])

    # Hidden fields
    department = HiddenField("Department", default="Engineering")
    trainees_data = HiddenField("Trainees Data")
    trainer_email = HiddenField("Trainer Email")  # New hidden field for trainer email
    trainer_department = HiddenField("Trainer Department")  # New hidden field for trainer department

    # Attachment fields
    attachments = MultipleFileField(
        "Attachments",
        validators=[RequiredAttachmentsIfVirtual("At least one attachment is required for virtual training.")],
        description="Required for virtual training",
    )  # Example: Make optional
    attachment_descriptions = TextAreaField(
        "Attachment Descriptions (one per line)", validators=[Optional()]
    )

    # Updated trainee field
    trainee_emails = TextAreaField(
        "Trainee Emails (comma/space separated)", validators=[Optional()]
    )

    # Submit Button
    submit = SubmitField("Submit Training Form")

    def validate(self, extra_validators=None):
        """Override validate to add debugging for form validation"""
        logger.debug("=== FORM VALIDATION START ===")
        logger.debug(f"Form data: {self.data}")
        
        # Call parent validation
        result = super().validate(extra_validators)
        
        logger.debug(f"Overall validation result: {result}")
        logger.debug(f"Form errors: {self.errors}")
        
        # Debug specific fields
        logger.debug(f"Location type value: {self.location_type.data}")
        logger.debug(f"Location type errors: {self.location_type.errors}")
        logger.debug(f"Training type value: {self.training_type.data}")
        logger.debug(f"Training type errors: {self.training_type.errors}")
        
        # Log all field errors
        for field_name, field in self._fields.items():
            if hasattr(field, 'errors') and field.errors:
                logger.debug(f"Field '{field_name}' has errors: {field.errors}")
        
        logger.debug("=== FORM VALIDATION END ===")
        return result

    def validate_location_type(self, field):
        """Custom validation method for location_type with debugging"""
        logger.debug(f"=== CUSTOM LOCATION VALIDATION ===")
        logger.debug(f"Location type field data: {field.data}")
        logger.debug(f"Location type field raw_data: {field.raw_data}")
        logger.debug(f"Location type field errors before custom validation: {field.errors}")
        
        # Let the DataRequired validator handle the actual validation
        # This is just for debugging
        if not field.data:
            logger.debug("Location type is empty - DataRequired should catch this")
        else:
            logger.debug(f"Location type has value: {field.data}")
        
        logger.debug(f"Location type field errors after custom validation: {field.errors}")
        logger.debug("=== END CUSTOM LOCATION VALIDATION ===")

    # --- Custom Validation Methods ---
    # Keep these for logic more complex than RequiredIf handles directly

    def validate_end_date(self, field):
        """Validate that end date is not before start date"""
        if self.start_date.data and field.data and field.data < self.start_date.data:
            raise ValidationError("End date cannot be earlier than start date.")

    # Keep concur and other expense validation here as they depend on multiple fields/values > 0
    def validate_concur_claim(self, field):
        """Validate that Concur Claim Number is provided when expenses > 0 are entered"""
        has_expenses = (
            (self.course_cost.data and self.course_cost.data > 0)
        )
        if has_expenses and (not field.data or not field.data.strip()):
            raise ValidationError(
                "Concur Claim Number is required when expenses are entered."
            )

    def validate_trainees_data(self, field):
        """Validate that at least one trainee has been added."""
        if not field.data or field.data.strip() == "[]":
            raise ValidationError("At least one trainee must be added.")

    def process_emails(self):
        """Process and clean the trainee emails"""
        if not self.trainee_emails.data:
            return []
        emails = re.split(r"[,\s]+", self.trainee_emails.data)
        return [email.strip() for email in emails if email.strip()]

    def prepare_form_data(self):
        """Prepare form data for database insertion"""
        is_internal = self.training_type.data == "Internal Training"
        data = {
            "training_type": self.training_type.data,
            "training_name": self.training_name.data,
            "trainer_name": (self.trainer_name.data if is_internal else None),
            "trainer_email": (self.trainer_email.data if is_internal else None),
            "trainer_department": (self.trainer_department.data if is_internal else None),
            "supplier_name": (self.supplier_name.data if not is_internal else None),
            "location_type": self.location_type.data,
            "location_details": (
                self.location_details.data
                if self.location_type.data == "Offsite"
                else None
            ),
            "start_date": self.start_date.data.strftime("%Y-%m-%d"),
            "end_date": self.end_date.data.strftime("%Y-%m-%d"),
            "training_hours": float(str(self.training_hours.data)),
            "course_cost": (
                float(self.course_cost.data)
                if not is_internal and self.course_cost.data is not None
                else 0.0
            ),
            "invoice_number": (
                self.invoice_number.data if not is_internal else None
            ),
            "concur_claim": self.concur_claim.data,
            "training_description": self.training_description.data or "",
            "notes": self.notes.data or "",
            "ida_class": self.ida_class.data,
        }

        # Note: trainees are now handled separately via the new Trainee table
        # No need to include trainees_data in the form data anymore
        
        return data




class InvoiceForm(FlaskForm):
    """Form for adding invoices"""

    invoice_number = StringField("Invoice Number", validators=[Optional()])
    cost = DecimalField(
        "Cost (€)", validators=[DataRequired(), NumberRange(min=0)], places=2
    )
    description = TextAreaField("Description", validators=[Optional()])
    attachment = FileField(
        "Invoice Attachment",
        validators=[
            Optional(),
            FileAllowed(list(ALLOWED_EXTENSIONS), "Only document files are allowed."),
        ],
    )
    submit = SubmitField("Add Invoice")


class SearchForm(FlaskForm):
    """Form for searching and filtering training submissions"""

    search = StringField("Search", validators=[Optional()])

    date_from = DateField("From Date", validators=[Optional()], format="%Y-%m-%d")

    date_to = DateField("To Date", validators=[Optional()], format="%Y-%m-%d")

    training_type = SelectField(
        "Training Type",
        choices=[("", "All Types")] + [(type, type) for type in TRAINING_TYPES],
        validators=[Optional()],
    )

    sort_by = SelectField("Sort By", choices=SORT_OPTIONS, default="submission_date")

    sort_order = SelectField(
        "Order",
        choices=[("DESC", "Newest First"), ("ASC", "Oldest First")],
        default="DESC",
    )

    approval_status = SelectField(
        "Approval Status",
        choices=APPROVAL_STATUS_OPTIONS,
        validators=[Optional()],
    )

    delete_status = SelectField(
        "Form Status",
        choices=[
            ("", "Not Deleted"),
            ("deleted", "Deleted"),
            ("all", "All Forms")
        ],
        validators=[Optional()],
        default=""
    )

    submit = SubmitField("Search")

    def validate_date_to(self, field):
        """Validate that to_date is not before from_date"""
        if field.data and self.date_from.data and field.data < self.date_from.data:
            raise ValidationError("To Date cannot be earlier than From Date.")


class LoginForm(FlaskForm):
    """Form for user login"""

    username = StringField("Username (Email)", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

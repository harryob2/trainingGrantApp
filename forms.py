from datetime import date
import re
import json
import logging
import time

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


class TrainingForm(FlaskForm):
    """Form for training submissions"""

    # Always Required
    training_type = RadioField(
        "Training Type",
        choices=[
            ("Internal Training", "Internal Training"),
            ("External Training", "External Training"),
        ]
                )
    training_name = StringField(
        "Training Name",
        description="The name/title of the training course",
    )
    location_type = RadioField(
        "Location",
        choices=[("Onsite", "Onsite"), ("Offsite", "Offsite"), ("Virtual", "Virtual")],
    )
    start_date = DateField(
        "Start Date", format="%Y-%m-%d", default=date.today
    )
    end_date = DateField(
        "End Date", format="%Y-%m-%d", default=date.today
    )
    training_description = TextAreaField(
        "Training Description"
    )
    notes = TextAreaField(
        "Notes for Reviewer", 
        description="Optional notes for the person reviewing this form submission"
    )
    ida_class = SelectField(
        "Training Class",
        choices=IDA_CLASS_CHOICES,
    )

    # Conditionally Required
    trainer_name = StringField(
        "Trainer Name",
        description="For internal training, select from employee list",
    )
    supplier_name = StringField(
        "Supplier Name",
        description="For external training, enter supplier name",
    )
    location_details = StringField(
        "Location Details",
        description="Required for offsite training",
    )
    training_hours = FloatField(
        "Training Hours",
        default=None,
        render_kw={"type": "number", "step": "0.1", "min": "0"},
    )
    course_cost = SmartFloatField(
        "Course Cost",
        default=None,
    )
    invoice_number = StringField(
        "Invoice Number",
        description="Invoice number for external training course",
    )
    concur_claim = StringField("Concur Claim Number")

    # Hidden fields
    department = HiddenField("Department", default="Engineering")
    trainees_data = HiddenField("Trainees Data")
    trainer_email = HiddenField("Trainer Email")  # New hidden field for trainer email
    trainer_department = HiddenField("Trainer Department")  # New hidden field for trainer department
    ready_for_approval = HiddenField("Ready for Approval")
    is_draft = HiddenField("Is Draft", default=False)

    # Attachment fields
    attachments = MultipleFileField(
        "Attachments",
        description="Required for virtual training",
    )  # Example: Make optional
    attachment_descriptions = TextAreaField(
        "Attachment Descriptions (one per line)"
    )

    # Updated trainee field
    trainee_emails = TextAreaField(
        "Trainee Emails (comma/space separated)"
    )

    # Submit Button
    submit = SubmitField("Submit Training Form")

    def process_emails(self):
        """Process and clean the trainee emails"""
        if not self.trainee_emails.data:
            return []
        emails = re.split(r"[,\s]+", self.trainee_emails.data)
        return [email.strip() for email in emails if email.strip()]

    def is_ready_for_approval(self):
        # first check if the form is a draft
        if self.is_draft.data:
            return False
        
        # Check for 'Not sure' ida_class specifically
        if self.ida_class.data and str(self.ida_class.data).strip().lower() == 'not sure':
            return False
        
        # Check if form is ready for approval by looking for flagged values
        flagged_values = ['NA', 'N/A', 'na', '1111', '€1111.00', '€1111', '1111.00', '1111.0']        
        
        fields_to_check = [
            self.training_name.data,
            self.trainer_name.data,
            self.supplier_name.data,
            self.location_details.data,
            self.training_description.data,
            self.training_hours.data,
            self.notes.data,
            self.invoice_number.data,
            self.concur_claim.data,
            self.ida_class.data,
            self.course_cost.data,
        ]
        
        for field_value in fields_to_check:
            if field_value and str(field_value).strip() in flagged_values:
                return False
        
        return True

    def prepare_form_data(self):
        """Prepare form data for database insertion"""
        is_internal = self.training_type.data == "Internal Training"
        
        # Date processing
        start_date_str = self.start_date.data.strftime("%Y-%m-%d")
        end_date_str = self.end_date.data.strftime("%Y-%m-%d")
        
        # Approval check
        ready_for_approval = self.is_ready_for_approval()
        
        # Data structure building
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
            "start_date": start_date_str,
            "end_date": end_date_str,
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
            "ready_for_approval": ready_for_approval,
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
            ("not_deleted", "Not Deleted"),
            ("deleted", "Deleted"),
            ("approved", "Approved"),
            ("unapproved", "Unapproved"),
            ("draft", "Draft"),
            ("all", "All Forms")
        ],
        validators=[Optional()],
        default="not_deleted"
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

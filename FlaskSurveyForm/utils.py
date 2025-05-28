"""
Utility functions for the training form application.

This module contains utility functions for handling file uploads and other common operations.
"""

import os
import logging
from datetime import datetime
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Import configuration
try:
    from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
except ImportError:
    # Fallback if config is not available
    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "jpg", "jpeg", "png", "txt"}
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "./uploads")

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if a filename has an allowed extension"""
    return (
        filename
        and "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


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


def get_quarter(dt):
    """
    Get quarter string from datetime object.
    
    Args:
        dt: datetime object
        
    Returns:
        str: Quarter string in format "Q1 2024", "Q2 2024", etc.
    """
    q = (dt.month - 1) // 3 + 1
    return f"Q{q} {dt.year}"


def prepare_form_data(form, request=None):
    """Prepare form data for database insertion"""
    logging.debug("=== Starting prepare_form_data ===")

    data = {
        "training_type": form.training_type.data,
        "supplier_name": (
            form.supplier_name.data
            if form.training_type.data == "External Training"
            else None
        ),
        "trainer_name": (
            form.trainer_name.data
            if form.training_type.data == "Internal Training"
            else None
        ),
        "location_type": form.location_type.data,
        "location_details": (
            form.location_details.data if form.location_type.data == "Offsite" else None
        ),
        "start_date": form.start_date.data,
        "end_date": form.end_date.data,
        "training_hours": (
            form.training_hours.data
            if form.training_type.data == "Internal Training"
            else None
        ),
        "trainees_data": "[]",
    }

    logging.debug(f"Initial data: {data}")

    # Handle trainees data if present
    if request and "trainees_data" in request.form:
        try:
            trainees_data = request.form["trainees_data"]
            logging.debug(f"Raw trainees data from form: {trainees_data}")
            if trainees_data:
                data["trainees_data"] = trainees_data
                logging.debug(f"Updated trainees data: {data['trainees_data']}")
        except Exception as e:
            logging.error(f"Error processing trainees data: {e}")
            logging.error(
                f"Raw trainees data that caused error: {request.form.get('trainees_data')}"
            )

    logging.debug(f"Final prepared data: {data}")
    logging.debug("=== End prepare_form_data ===")
    return data

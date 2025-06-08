"""
Email utility functions for the training form application.

This module handles sending email notifications for form submissions.
"""

import logging
from datetime import datetime
from flask import current_app
from flask_mail import Mail, Message


# Initialize Flask-Mail instance
mail = Mail()


def init_mail(app):
    """Initialize Flask-Mail with the given Flask app"""
    mail.init_app(app)


def send_form_submission_notification(form_id, form_data, submitter_email):
    """
    Send email notification when a training form is submitted.
    
    Args:
        form_id (int): The ID of the submitted form
        form_data (dict): The form data containing training details
        submitter_email (str): Email of the person who submitted the form
    """
    try:
        # Skip sending emails for test user to prevent spam during automated testing
        if submitter_email == 'harry@test.com':
            logging.info(f"Skipping email notification for test user: {submitter_email}")
            return
        
        # Determine notification emails based on environment
        flask_env = current_app.config.get('FLASK_ENV', 'development')
        
        if flask_env == 'production':
            # Production: send to admins who want to receive emails
            from models import get_admin_notification_emails
            notification_emails = get_admin_notification_emails()
            if not notification_emails:
                logging.warning("No admins configured to receive email notifications in production")
                return
        else:
            # Development/staging: send only to Harry
            notification_emails = ['harry.obrien@stryker.com']
        
        logging.info(f"Sending form notification for environment '{flask_env}' to: {', '.join(notification_emails)}")
        
        # Get trainee count from database
        try:
            from models import get_trainees
            trainees = get_trainees(form_id)
            trainee_count = len(trainees)
        except Exception as e:
            logging.error(f"Error getting trainees for form {form_id}: {e}")
            trainee_count = 0
        
        # Determine if training is internal or external
        training_type = form_data.get('training_type', 'Unknown')
        is_external = training_type == 'External Training'
        
        # Create email subject
        subject = f"New Training Form Submitted - {training_type}"
        
        # Create HTML body
        html_body = f"""
        <html>
        <body>
            <h2>New Training Form Submitted</h2>
            <p>A new training form has been submitted and requires your attention.</p>
            
            <h3>Form Details:</h3>
            <ul>
                <li><strong>Submitted by:</strong> {submitter_email}</li>
                <li><strong>Training Type:</strong> {training_type}</li>
                <li><strong>Training Name:</strong> {form_data.get('training_name', 'N/A')}</li>
                <li><strong>Training Date:</strong> {form_data.get('start_date', 'N/A')}</li>
                <li><strong>Training Location:</strong> {form_data.get('location_type', 'N/A')}"""
        
        # Add location details if offsite
        if form_data.get('location_details'):
            html_body += f" - {form_data.get('location_details')}"
            
        html_body += f"""</li>
                <li><strong>Number of Trainees:</strong> {trainee_count}</li>"""

        # Add external training specific info
        if is_external:
            html_body += f"""
                <li><strong>External Vendor:</strong> {form_data.get('supplier_name', 'N/A')}</li>
                <li><strong>Training Cost:</strong> €{form_data.get('course_cost', 0):.2f}</li>"""
        
        # Add notes if any
        notes = form_data.get('notes', '').strip()
        if notes:
            html_body += f"""
                <li><strong>Notes for Reviewer:</strong> {notes}</li>"""

        html_body += """
            </ul>
            
            <p>You can log in to the training application to review and approve this form <a href="http://azulimpbi01:5000">by clicking this link.</a></p>
            
            <p><em>This is an automated notification from the Training Form Application.</em></p>
        </body>
        </html>
        """
        
        # Create and send the message
        msg = Message(
            subject=subject,
            recipients=notification_emails,
            html=html_body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        
        mail.send(msg)
        logging.info(f"Form submission notification sent for form {form_id} to {', '.join(notification_emails)}")
        
    except Exception as e:
        logging.error(f"Failed to send form submission notification for form {form_id}: {e}")
        # Don't raise the exception to avoid breaking form submission 
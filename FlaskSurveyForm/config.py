"""
Configuration settings for the training form application.

This module contains configuration settings for the application,
including database connection details, file upload settings, and other parameters.
"""

import os

# Application settings
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-secret-key")  # For CSRF protection

# File upload settings
# UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', './uploads')
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB max upload size
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "jpg", "jpeg", "png", "txt"}

# SQLite database settings (for development/testing)
DB_PATH = os.environ.get("DB_PATH", "training_forms.db")

# MariaDB/MySQL database settings (for production)
# These would be used when connecting to the azulimpbi01 server
DB_HOST = os.environ.get("DB_HOST", "azulimpbi01")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_NAME = os.environ.get("DB_NAME", "analysis")
DB_USER = os.environ.get("DB_USER", "admin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "Mfg#13579")

# Network file storage settings
# This is the path where invoice attachments would be saved in production
NETWORK_STORAGE_PATH = os.environ.get(
    "NETWORK_STORAGE_PATH",
    "\\\\strykercorp.com\\lim\\Engineering_DOG\\5. Automation & Controls\\01. Projects\\Training Form Invoices",
)

# Determine if we should use SQLite or MariaDB
USE_SQLITE = os.environ.get("USE_SQLITE", "True").lower() == "true"

# Database URL construction
if USE_SQLITE:
    DATABASE_URL = f"sqlite:///{DB_PATH}"
else:
    DATABASE_URL = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

# Flask-WTF settings
WTF_CSRF_ENABLED = True

# Database configuration
DATABASE = "training_forms.db"

# Upload folder configuration
UPLOAD_FOLDER = "uploads"

# Debug mode
DEBUG = True  # Set to False in production

# LDAP Configuration (Based on working Go app configuration)
LDAP_HOST = "limdc02.strykercorp.com"
LDAP_PORT = 3268
LDAP_BASE_DN = "DC=strykercorp,DC=com"
LDAP_DOMAIN = "strykercorp.com"
LDAP_USE_SSL = False

# Group membership requirement (leave empty to disable group checking)
LDAP_REQUIRED_GROUP = ""  # Set to group name if you want to restrict access to specific group

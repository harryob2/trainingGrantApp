"""
Configuration settings for the training form application.

This module contains configuration settings for the application,
including database connection details, file upload settings, and other parameters.
"""

import os
from pathlib import Path

# Load environment file based on FLASK_ENV
def load_env_file():
    """Load environment variables from .env file based on FLASK_ENV"""
    flask_env = os.environ.get('FLASK_ENV', 'development')
    env_file = f'.env.{flask_env}'
    
    if os.path.exists(env_file):
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"Loaded environment from {env_file}")
    elif os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv('.env')
        print("Loaded environment from .env")
    else:
        print(f"No environment file found. Using system environment variables.")

# Try to load environment file
try:
    load_env_file()
except ImportError:
    print("python-dotenv not installed. Using system environment variables only.")

# Application settings
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
SECRET_KEY = os.environ.get("SECRET_KEY", os.environ.get("SESSION_SECRET", "dev-secret-key"))

# File upload settings
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB max upload size
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "jpg", "jpeg", "png", "csv", "txt"}

# SQLite database settings (for development/testing)
DB_PATH = os.environ.get("DB_PATH", "training_forms.db")

# MariaDB/MySQL database settings (for production)
DB_HOST = os.environ.get("DB_HOST", "azulimpbi01")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_NAME = os.environ.get("DB_NAME", "training_tool")  # Updated to use training_tool database
DB_USER = os.environ.get("DB_USER", "admin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "Mfg#13579")

# Network file storage settings (for production)
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
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Flask-WTF settings
WTF_CSRF_ENABLED = True

# LDAP Configuration
LDAP_HOST = os.environ.get("LDAP_HOST", "limdc02.strykercorp.com")
LDAP_PORT = int(os.environ.get("LDAP_PORT", "3268"))
LDAP_BASE_DN = os.environ.get("LDAP_BASE_DN", "DC=strykercorp,DC=com")
LDAP_DOMAIN = os.environ.get("LDAP_DOMAIN", "strykercorp.com")
LDAP_USE_SSL = os.environ.get("LDAP_USE_SSL", "False").lower() == "true"
LDAP_REQUIRED_GROUP = os.environ.get("LDAP_REQUIRED_GROUP", "")

# Email Configuration
MAIL_SERVER = 'syksmtp.strykercorp.com'
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = None  # Usually not needed for internal SMTP
MAIL_PASSWORD = None  # Usually not needed for internal SMTP
MAIL_DEFAULT_SENDER = 'training-app@strykercorp.com'

# Environment-specific settings
FLASK_ENV = os.environ.get("FLASK_ENV", "development")
IS_PRODUCTION = FLASK_ENV == "production"

# Print configuration summary (for debugging)
if DEBUG:
    print(f"Environment: {FLASK_ENV}")
    print(f"Database: {'SQLite' if USE_SQLITE else 'MariaDB'}")
    print(f"Database URL: {DATABASE_URL.replace(DB_PASSWORD, '***') if not USE_SQLITE else DATABASE_URL}")

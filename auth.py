"""
Authentication module for the training form application.

This module handles user authentication via LDAP and Flask-Login integration.
"""

import logging
import os
import functools
from flask import flash
from flask_login import LoginManager, UserMixin
import hashlib
import ldap3
from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
from models import db_session, get_admin_by_email

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize login manager
login_manager = LoginManager()

# Admin user configuration
ADMIN_BYPASS_USERS = {
    "harry@test.com": hashlib.sha256("cork4liam".encode()).hexdigest(),
    "user@test.com": hashlib.sha256("cork4liam".encode()).hexdigest(),
}


def is_admin_email(email):
    return email and get_admin_by_email(email) is not None


class User(UserMixin):
    """User class for Flask-Login."""

    def __init__(
        self,
        username,
        display_name=None,
        email=None,
        first_name=None,
        last_name=None,
        is_admin=False,
    ):
        self.id = username  # For Flask-Login, id is required
        self.username = username
        self.display_name = display_name or username.split("@")[0]
        self.email = email or username
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = is_admin

    @staticmethod
    def get(username):
        """Get user by username."""
        is_admin = is_admin_email(username)
        
        # Try to get user data from session first
        from flask import session
        first_name = session.get('user_first_name')
        last_name = session.get('user_last_name')
        
        user = User(
            username=username,
            display_name=username.split("@")[0],
            email=username,
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin
        )
        
        # Profile pictures are handled client-side to avoid session size limits
        user.profile_picture = None
        
        return user


def init_auth(app):
    """Initialize authentication with the Flask app."""
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    # Register user loader callback
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)


def verify_ldap_user(username, password, app_config):
    """
    Verify user credentials against LDAP using direct ldap3 library.
    Based on the working Go implementation.
    """
    logger.info(f"Verifying user: {username}")
    
    # LDAP configuration from app config
    ldap_host = app_config.get('LDAP_HOST', 'limdc02.strykercorp.com')
    ldap_port = app_config.get('LDAP_PORT', 3268)
    ldap_base = app_config.get('LDAP_BASE_DN', 'DC=strykercorp,DC=com')
    ldap_domain = app_config.get('LDAP_DOMAIN', 'strykercorp.com')
    ldap_use_ssl = app_config.get('LDAP_USE_SSL', False)
    required_group = app_config.get('LDAP_REQUIRED_GROUP', '')
    
    try:
        # Connect to LDAP server
        logger.info(f"Connecting to LDAP server: {ldap_host}:{ldap_port}")
        server_uri = f"{'ldaps' if ldap_use_ssl else 'ldap'}://{ldap_host}:{ldap_port}"
        server = Server(server_uri, get_info=ALL)
        
        # Create connection and bind with user credentials
        logger.info(f"Authenticating with LDAP for user: {username}")
        conn = Connection(server, user=username, password=password, auto_bind=True)
        
        logger.info(f"User {username} authenticated successfully")
        
        # Search for user's DN to get user details
        user_filter = f"(&(objectClass=person)(userPrincipalName={username}))"
        logger.info(f"Searching for user DN with filter: {user_filter}")
        
        conn.search(
            search_base=ldap_base,
            search_filter=user_filter,
            search_scope=SUBTREE,
            attributes=['displayName', 'mail', 'givenName', 'sn', 'userPrincipalName', 'distinguishedName']
        )
        
        if not conn.entries:
            logger.error(f"User not found in LDAP directory: {username}")
            return None, "User not found in LDAP"
        
        # Get user details from first entry
        user_entry = conn.entries[0]
        user_dn = str(user_entry.distinguishedName)
        logger.info(f"Found user DN: {user_dn}")
        
        # Check group membership if required
        if required_group:
            logger.info(f"Checking if user is in group: {required_group}")
            
            # Search for group membership
            group_filter = f"(&(objectClass=group)(cn={required_group})(member={user_dn}))"
            logger.info(f"Group membership filter: {group_filter}")
            
            conn.search(
                search_base=ldap_base,
                search_filter=group_filter,
                search_scope=SUBTREE,
                attributes=['cn']
            )
            
            if not conn.entries:
                error_msg = f"User not in required group: {required_group}"
                logger.error(error_msg)
                conn.unbind()
                return None, "User not in required group"
            
            logger.info(f"User {username} is a member of group {required_group}")
        
        # Create user object with LDAP attributes
        user_data = {
            'username': username,
            'dn': user_dn,
            'display_name': str(user_entry.displayName) if user_entry.displayName else username.split('@')[0],
            'email': str(user_entry.mail) if user_entry.mail else username,
            'first_name': str(user_entry.givenName) if user_entry.givenName else None,
            'last_name': str(user_entry.sn) if user_entry.sn else None,
            'is_admin': is_admin_email(username)
        }
        
        conn.unbind()
        logger.info(f"LDAP verification completed successfully for user {username}")
        return user_data, None
        
    except ldap3.core.exceptions.LDAPBindError as e:
        logger.error(f"LDAP authentication failed for {username}: {str(e)}")
        return None, "Incorrect Username or Password"
    except ldap3.core.exceptions.LDAPException as e:
        logger.error(f"LDAP error for {username}: {str(e)}")
        return None, "LDAP connection error. Please ensure you are on the Stryker network and try again."
    except Exception as e:
        logger.error(f"Unexpected error during LDAP authentication for {username}: {str(e)}")
        return None, "Authentication error. Please contact support."


def authenticate_user(username, password, app_config=None):
    """Authenticate a user with LDAP or bypass credentials."""
    username_lc = username.lower()
    
    # Check for admin bypass users first
    if username_lc in ADMIN_BYPASS_USERS:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash == ADMIN_BYPASS_USERS[username_lc]:
            logger.info(f"Bypass user {username} authenticated successfully")
            
            # Store basic user info in session for bypass users
            from flask import session
            session['user_first_name'] = "Test"
            session['user_last_name'] = "User"
            
            # Profile pictures are handled client-side to avoid session size limits
            # (Flask sessions are stored in browser cookies with ~4KB limit)
            session.pop('user_profile_picture', None)
            
            return User.get(username)
        else:
            logger.warning(f"Failed bypass login attempt for {username}")
            flash("Invalid password.", "danger")
            return None

    # If not admin bypass, try LDAP authentication
    if not app_config:
        logger.error("App config not provided for LDAP authentication")
        flash("Configuration error. Please contact support.", "danger")
        return None
    
    user_data, error_msg = verify_ldap_user(username, password, app_config)
    
    if user_data:
        # Store user information in session for later retrieval
        from flask import session
        session['user_first_name'] = user_data['first_name']
        session['user_last_name'] = user_data['last_name']
        
        # Profile pictures are handled client-side to avoid session size limits
        # (Flask sessions are stored in browser cookies with ~4KB limit)
        session.pop('user_profile_picture', None)
        
        # Create and return user object
        user = User(
            username=user_data['username'],
            display_name=user_data['display_name'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            is_admin=user_data['is_admin']
        )
        logger.info(f"User created: {user.username}, Name: {user.display_name}")
        return user
    else:
        # Authentication failed
        logger.warning(f"Authentication failed for {username}: {error_msg}")
        flash(error_msg or "Authentication failed.", "danger")
        return None

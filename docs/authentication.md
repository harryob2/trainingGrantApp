# Authentication System Documentation

## Overview

The Flask Survey Form System implements a comprehensive authentication and authorization system using LDAP integration for corporate directory authentication, Flask-Login for session management, and role-based access control for administrative functions.

## Authentication Architecture

### Components

1. **LDAP Integration** (`auth.py`): Corporate directory authentication
2. **Flask-Login** (`auth.py`): Session management and user state
3. **User Model** (`auth.py`): User representation and role management
4. **Admin Management** (`models.py`): Administrative user database
5. **Route Protection** (`app.py`): Decorator-based access control

### Authentication Flow

```
User Login → LDAP Verification → User Object Creation → Session Creation → Role Assignment → Access Control
```

## LDAP Authentication

### Configuration

**LDAP Settings** (`config.py`):
```python
LDAP_HOST = "limdc02.strykercorp.com"
LDAP_PORT = 3268
LDAP_BASE_DN = "DC=strykercorp,DC=com"
LDAP_DOMAIN = "strykercorp.com"
LDAP_USE_SSL = False
LDAP_REQUIRED_GROUP = ""  # Optional group membership requirement
```

### LDAP Authentication Process

#### 1. Connection Establishment
```python
def verify_ldap_user(username, password, app_config):
    # Connect to LDAP server
    server_uri = f"{'ldaps' if ldap_use_ssl else 'ldap'}://{ldap_host}:{ldap_port}"
    server = Server(server_uri, get_info=ALL)
    
    # Create connection and bind with user credentials
    conn = Connection(server, user=username, password=password, auto_bind=True)
```

#### 2. User Verification
```python
# Search for user's DN to get user details
user_filter = f"(&(objectClass=person)(userPrincipalName={username}))"
conn.search(
    search_base=ldap_base,
    search_filter=user_filter,
    search_scope=SUBTREE,
    attributes=['displayName', 'mail', 'givenName', 'sn', 'userPrincipalName', 'distinguishedName']
)
```

#### 3. Group Membership Check (Optional)
```python
if required_group:
    group_filter = f"(&(objectClass=group)(cn={required_group})(member={user_dn}))"
    conn.search(
        search_base=ldap_base,
        search_filter=group_filter,
        search_scope=SUBTREE,
        attributes=['cn']
    )
```

### LDAP Error Handling

**Authentication Errors**:
- `LDAPBindError`: Invalid credentials
- `LDAPException`: Connection or server errors
- `Exception`: Unexpected errors

**Error Messages**:
- "Incorrect Username or Password"
- "LDAP connection error. Please ensure you are on the Stryker network and try again."
- "User not found in LDAP"
- "User not in required group"

## User Model

### User Class Definition

```python
class User(UserMixin):
    def __init__(self, username, dn=None, display_name=None, email=None, 
                 first_name=None, last_name=None, groups=None, is_admin=False):
        self.id = username  # Required for Flask-Login
        self.username = username
        self.dn = dn
        self.display_name = display_name or username.split("@")[0]
        self.email = email or username
        self.first_name = first_name
        self.last_name = last_name
        self.groups = groups or []
        self.is_admin = is_admin
```

### User Attributes

- **id**: Unique identifier (username/email) for Flask-Login
- **username**: User's login name (email address)
- **dn**: LDAP Distinguished Name
- **display_name**: Human-readable name for UI display
- **email**: User's email address
- **first_name**: User's first name from LDAP
- **last_name**: User's last name from LDAP
- **groups**: LDAP group memberships (future use)
- **is_admin**: Administrative privilege flag

### User Factory Method

```python
@staticmethod
def get(username):
    """Get user by username with admin status check"""
    is_admin = is_admin_email(username)
    display_name = "Administrator" if is_admin else username.split("@")[0]
    return User(
        username=username,
        display_name=display_name,
        email=username,
        first_name="Admin" if is_admin else None,
        last_name="User" if is_admin else None,
        is_admin=is_admin,
    )
```

## Session Management

### Flask-Login Integration

#### Initialization
```python
def init_auth(app):
    """Initialize authentication with the Flask app"""
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"
```

#### User Loader
```python
@login_manager.user_loader
def load_user(user_id):
    """Load user from session"""
    return User.get(user_id)
```

### Session Security

**Configuration**:
- **Secure Cookies**: HTTPS-only session cookies in production
- **Session Timeout**: Configurable session expiration
- **CSRF Protection**: Cross-site request forgery prevention
- **Session Regeneration**: New session ID on login

**Session Data**:
- User ID (email address)
- Authentication timestamp
- Role information
- CSRF tokens

## Authorization System

### Role-Based Access Control

#### Admin Role Definition
```python
def is_admin_email(email):
    """Check if email belongs to an admin user"""
    return email and get_admin_by_email(email) is not None

def is_admin_user(user):
    """Check if user has admin privileges"""
    return hasattr(user, "email") and is_admin_email(user.email)
```

#### Admin Database Model
```python
class Admin(Base):
    __tablename__ = "admins"
    email = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
```

### Access Control Decorators

#### Authentication Required
```python
@login_required
def protected_route():
    """Route requiring authentication"""
    pass
```

#### Admin Required
```python
def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_user(current_user):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_required
def admin_only_route():
    """Route requiring admin privileges"""
    pass
```

### Resource-Level Authorization

#### Form Access Control
```python
def can_edit_form(user, form):
    """Check if user can edit a specific form"""
    # Users can edit their own unapproved forms
    if form.submitter == user.email and not form.approved:
        return True
    # Admins can edit any form
    if is_admin_user(user):
        return True
    return False

def can_view_form(user, form):
    """Check if user can view a specific form"""
    # Users can view their own forms
    if form.submitter == user.email:
        return True
    # Admins can view any form
    if is_admin_user(user):
        return True
    # Other users can view approved forms
    if form.approved:
        return True
    return False
```

## Bypass Authentication (Development)

### Test User Accounts

For development and testing purposes, the system includes bypass authentication:

```python
ADMIN_BYPASS_USERS = {
    "harry@test.com": hashlib.sha256("cork4liam".encode()).hexdigest(),
    "user@test.com": hashlib.sha256("cork4liam".encode()).hexdigest(),
}
```

### Bypass Authentication Flow
```python
def authenticate_user(username, password, app_config=None):
    username_lc = username.lower()
    
    # Check for admin bypass users first
    if username_lc in ADMIN_BYPASS_USERS:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash == ADMIN_BYPASS_USERS[username_lc]:
            return User.get(username)
    
    # Fall back to LDAP authentication
    return ldap_authenticate(username, password, app_config)
```

## Security Features

### Password Security
- **No Local Storage**: Passwords never stored in application database
- **LDAP Delegation**: Password verification delegated to LDAP server
- **Secure Transmission**: Passwords transmitted securely to LDAP server
- **Hash Verification**: Bypass accounts use SHA-256 hashed passwords

### Session Security
- **Secure Cookies**: HTTPOnly and Secure flags in production
- **Session Regeneration**: New session ID on successful login
- **Automatic Logout**: Session expiration and cleanup
- **CSRF Protection**: Token-based CSRF prevention

### Access Control Security
- **Principle of Least Privilege**: Users have minimal required access
- **Resource Ownership**: Users can only access their own data
- **Admin Separation**: Clear separation between user and admin roles
- **Route Protection**: All sensitive routes protected by decorators

## Login Process

### User Login Flow

1. **Login Page Display**
   ```python
   @app.route("/login", methods=["GET", "POST"])
   def login():
       if current_user.is_authenticated:
           return redirect(url_for("index"))
   ```

2. **Credential Submission**
   ```python
   form = LoginForm()
   if form.validate_on_submit():
       username = form.username.data
       password = form.password.data
   ```

3. **Domain Handling**
   ```python
   if "@" not in username and app.config.get("LDAP_DOMAIN"):
       username = f"{username}@{app.config['LDAP_DOMAIN']}"
   ```

4. **Authentication**
   ```python
   user = authenticate_user(username, password, app.config)
   ```

5. **Session Creation**
   ```python
   if user:
       login_user(user)
       next_page = request.args.get("next")
       return redirect(next_page or url_for("index"))
   ```

### Logout Process

```python
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))
```

## Admin Management

### Admin User Operations

#### Add Admin
```python
def add_admin(admin_data):
    """Add a new admin to the database"""
    with db_session() as session:
        if session.query(Admin).filter_by(email=admin_data["email"]).first():
            return False  # Admin already exists
        admin = Admin(
            email=admin_data["email"],
            first_name=admin_data["first_name"],
            last_name=admin_data["last_name"],
        )
        session.add(admin)
        return True
```

#### Remove Admin
```python
@app.route("/manage_admins", methods=["POST"])
@admin_required
def manage_admins():
    if "remove_admin" in request.form:
        email = request.form["remove_admin"].strip().lower()
        with db_session() as session:
            admin = session.query(Admin).filter_by(email=email).first()
            if admin:
                session.delete(admin)
```

#### List Admins
```python
def get_admin_by_email(email):
    """Retrieve an admin by their email"""
    with db_session() as session:
        admin = session.query(Admin).filter_by(email=email).first()
        if admin:
            return {
                "email": admin.email,
                "first_name": admin.first_name,
                "last_name": admin.last_name,
            }
        return None
```

## Error Handling

### Authentication Errors

#### LDAP Connection Errors
```python
except ldap3.core.exceptions.LDAPBindError as e:
    logger.error(f"LDAP authentication failed for {username}: {str(e)}")
    return None, "Incorrect Username or Password"

except ldap3.core.exceptions.LDAPException as e:
    logger.error(f"LDAP error for {username}: {str(e)}")
    return None, "LDAP connection error. Please ensure you are on the Stryker network and try again."
```

#### Authorization Errors
```python
@app.errorhandler(403)
def forbidden(e):
    flash("You don't have permission to access this resource.", "danger")
    return redirect(request.referrer or url_for("index"))
```

### Security Logging

```python
# Successful login
logging.info(f"User {username} logged in successfully")

# Failed login attempt
logging.warning(f"Failed login attempt for {username}")

# Admin actions
logging.info(f"Admin {current_user.email} approved form {form_id}")
```

## Configuration

### Environment Variables

```python
# LDAP Configuration
LDAP_HOST = os.environ.get("LDAP_HOST", "limdc02.strykercorp.com")
LDAP_PORT = int(os.environ.get("LDAP_PORT", "3268"))
LDAP_BASE_DN = os.environ.get("LDAP_BASE_DN", "DC=strykercorp,DC=com")
LDAP_DOMAIN = os.environ.get("LDAP_DOMAIN", "strykercorp.com")
LDAP_USE_SSL = os.environ.get("LDAP_USE_SSL", "False").lower() == "true"
LDAP_REQUIRED_GROUP = os.environ.get("LDAP_REQUIRED_GROUP", "")

# Session Configuration
SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-secret-key")
```

### Production Considerations

#### Security Hardening
- **HTTPS Only**: Force HTTPS in production
- **Secure Headers**: Implement security headers
- **Session Timeout**: Configure appropriate session timeouts
- **Rate Limiting**: Implement login attempt rate limiting

#### LDAP Configuration
- **SSL/TLS**: Use encrypted LDAP connections
- **Service Account**: Use dedicated service account for LDAP queries
- **Group Restrictions**: Implement group-based access control
- **Connection Pooling**: Optimize LDAP connection management

#### Monitoring
- **Authentication Logs**: Monitor login attempts and failures
- **Admin Actions**: Log all administrative actions
- **Security Events**: Alert on suspicious authentication patterns
- **Performance Monitoring**: Track authentication response times 
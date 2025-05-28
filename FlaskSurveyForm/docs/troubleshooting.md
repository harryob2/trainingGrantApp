# Troubleshooting Guide

## Overview

This guide provides solutions for common issues encountered when using, deploying, or maintaining the Flask Survey Form System. Issues are organized by category with step-by-step resolution procedures.

## Authentication Issues

### LDAP Connection Problems

#### Issue: "LDAP connection error. Please ensure you are on the Stryker network and try again."

**Symptoms**:
- Users cannot log in
- Error appears immediately after entering credentials
- Works for some users but not others

**Possible Causes**:
1. Network connectivity issues
2. LDAP server configuration problems
3. Firewall blocking LDAP traffic
4. Incorrect LDAP settings

**Resolution Steps**:

1. **Check Network Connectivity**:
   ```bash
   # Test LDAP server connectivity
   telnet limdc02.strykercorp.com 3268
   
   # Check DNS resolution
   nslookup limdc02.strykercorp.com
   ```

2. **Verify LDAP Configuration** (`config.py`):
   ```python
   LDAP_HOST = "limdc02.strykercorp.com"
   LDAP_PORT = 3268
   LDAP_BASE_DN = "DC=strykercorp,DC=com"
   LDAP_DOMAIN = "strykercorp.com"
   ```

3. **Check Application Logs**:
   ```bash
   # Look for LDAP-related errors
   grep -i "ldap" app.log
   grep -i "authentication" app.log
   ```

4. **Test with Bypass Account**:
   ```python
   # Use test account to verify application functionality
   username: harry@test.com
   password: cork4liam
   ```

#### Issue: "User not found in LDAP"

**Symptoms**:
- Specific users cannot log in
- Other users can authenticate successfully
- User exists in Active Directory

**Resolution Steps**:

1. **Verify User Principal Name**:
   - Ensure user is using full email address
   - Check for typos in username

2. **Check LDAP Search Base**:
   ```python
   # Verify search base includes user's OU
   LDAP_BASE_DN = "DC=strykercorp,DC=com"
   ```

3. **Test LDAP Query**:
   ```python
   # Manual LDAP search test
   user_filter = f"(&(objectClass=person)(userPrincipalName={username}))"
   ```

### Session Management Issues

#### Issue: Users logged out unexpectedly

**Symptoms**:
- Users redirected to login page during active use
- Session appears to expire quickly
- Inconsistent session behavior

**Resolution Steps**:

1. **Check Session Configuration**:
   ```python
   # Verify session settings
   app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
   app.config['SESSION_COOKIE_SECURE'] = True  # Only for HTTPS
   ```

2. **Review Server Logs**:
   ```bash
   # Look for session-related errors
   grep -i "session" app.log
   grep -i "csrf" app.log
   ```

3. **Clear Browser Cache**:
   - Instruct users to clear browser cache and cookies
   - Test in incognito/private browsing mode

## Database Issues

### Connection Problems

#### Issue: "Database connection failed"

**Symptoms**:
- Application fails to start
- Database operations fail
- Error messages about database connectivity

**Resolution Steps**:

1. **Check Database File** (SQLite):
   ```bash
   # Verify database file exists and is readable
   ls -la training_forms.db
   sqlite3 training_forms.db ".tables"
   ```

2. **Verify Database Configuration**:
   ```python
   # Check database URL
   DATABASE_URL = "sqlite:///training_forms.db"
   # or for MariaDB
   DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
   ```

3. **Test Database Connection**:
   ```python
   # Test connection manually
   from models import db_session
   try:
       with db_session() as session:
           result = session.execute("SELECT 1")
           print("Database connection successful")
   except Exception as e:
       print(f"Database connection failed: {e}")
   ```

4. **Recreate Database**:
   ```bash
   # Backup existing database
   cp training_forms.db training_forms_backup.db
   
   # Recreate database
   python setup_db.py
   ```

### Data Integrity Issues

#### Issue: "Foreign key constraint failed"

**Symptoms**:
- Error when deleting forms or attachments
- Database operations fail with constraint errors

**Resolution Steps**:

1. **Check Referential Integrity**:
   ```sql
   -- Find orphaned attachments
   SELECT * FROM attachments 
   WHERE form_id NOT IN (SELECT id FROM training_forms);
   
   -- Find forms with missing submitters
   SELECT * FROM training_forms 
   WHERE submitter NOT IN (SELECT email FROM admins);
   ```

2. **Clean Up Orphaned Records**:
   ```sql
   -- Remove orphaned attachments
   DELETE FROM attachments 
   WHERE form_id NOT IN (SELECT id FROM training_forms);
   ```

3. **Verify Cascade Settings**:
   ```python
   # Ensure proper cascade configuration
   attachments = relationship("Attachment", back_populates="training_form", 
                            cascade="all, delete-orphan")
   ```

## File Upload Issues

### Upload Failures

#### Issue: "File upload failed"

**Symptoms**:
- Files not uploading despite valid format
- Upload process hangs or times out
- Error messages about file handling

**Resolution Steps**:

1. **Check File Size Limits**:
   ```python
   # Verify file size configuration
   MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB
   ```

2. **Verify Upload Directory**:
   ```bash
   # Check upload directory permissions
   ls -la uploads/
   mkdir -p uploads/
   chmod 755 uploads/
   ```

3. **Check Disk Space**:
   ```bash
   # Verify available disk space
   df -h
   du -sh uploads/
   ```

4. **Test File Upload Manually**:
   ```python
   from utils import save_file, allowed_file
   
   # Test file validation
   print(allowed_file("test.pdf"))  # Should return True
   print(allowed_file("test.exe"))  # Should return False
   ```

#### Issue: "File type not allowed"

**Symptoms**:
- Valid file types rejected
- Inconsistent file type validation

**Resolution Steps**:

1. **Check Allowed Extensions**:
   ```python
   ALLOWED_EXTENSIONS = {
       "pdf", "doc", "docx", "xls", "xlsx", 
       "jpg", "jpeg", "png", "csv", "txt"
   }
   ```

2. **Verify File Extension**:
   ```python
   # Debug file extension detection
   filename = "document.PDF"  # Case sensitivity issue
   extension = filename.rsplit(".", 1)[1].lower()
   print(f"Extension: {extension}")
   ```

3. **Update File Validation**:
   ```python
   def allowed_file(filename):
       return (filename and "." in filename and 
               filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS)
   ```

### File Access Issues

#### Issue: "File not found" or "Access denied"

**Symptoms**:
- Uploaded files cannot be downloaded
- 404 errors when accessing files
- Permission denied errors

**Resolution Steps**:

1. **Check File Permissions**:
   ```bash
   # Verify file permissions
   ls -la uploads/form_*/
   chmod 644 uploads/form_*/*
   ```

2. **Verify File Path Structure**:
   ```bash
   # Check directory structure
   find uploads/ -type f -name "*.pdf" | head -5
   ```

3. **Test File Access**:
   ```python
   # Test file serving route
   from app import app
   with app.test_client() as client:
       response = client.get('/uploads/form_123/test.pdf')
       print(f"Status: {response.status_code}")
   ```

## Form Validation Issues

### Dynamic Validation Problems

#### Issue: Required fields not validating correctly

**Symptoms**:
- Fields marked as required but validation passes
- Conditional validation not working
- Form submission succeeds with missing data

**Resolution Steps**:

1. **Check Dynamic Validator**:
   ```python
   # Verify DynamicRequiredIf implementation
   def DynamicRequiredIf(condition_field, condition_value, additional_validator=None):
       def _validator(form, field):
           other_field = getattr(form, condition_field)
           if other_field.data == condition_value:
               field.validators = [DataRequired()]
           else:
               field.validators = [Optional()]
       return _validator
   ```

2. **Test Form Validation**:
   ```python
   # Manual form validation test
   from forms import TrainingForm
   form = TrainingForm()
   form.training_type.data = "Internal Training"
   form.trainer_name.data = ""  # Should fail validation
   
   if not form.validate():
       print("Validation errors:", form.errors)
   ```

3. **Check JavaScript Validation**:
   ```javascript
   // Verify client-side validation
   document.getElementById('training_type').addEventListener('change', function() {
       // Update required fields based on selection
   });
   ```

### CSRF Token Issues

#### Issue: "CSRF token missing or invalid"

**Symptoms**:
- Form submissions fail with CSRF errors
- Users see "The CSRF token is missing" message
- Forms work intermittently

**Resolution Steps**:

1. **Verify CSRF Configuration**:
   ```python
   # Check CSRF settings
   app.config['WTF_CSRF_ENABLED'] = True
   app.config['SECRET_KEY'] = 'your-secret-key'
   ```

2. **Check Template Implementation**:
   ```html
   <!-- Ensure CSRF token is included -->
   {{ form.hidden_tag() }}
   ```

3. **Debug CSRF Token**:
   ```python
   # Check if CSRF token is generated
   from flask_wtf.csrf import generate_csrf
   token = generate_csrf()
   print(f"CSRF Token: {token}")
   ```

## Performance Issues

### Slow Page Loading

#### Issue: Application responds slowly

**Symptoms**:
- Pages take long time to load
- Database queries are slow
- High server resource usage

**Resolution Steps**:

1. **Check Database Performance**:
   ```sql
   -- Analyze slow queries
   EXPLAIN QUERY PLAN SELECT * FROM training_forms WHERE submitter = 'user@example.com';
   
   -- Add missing indexes
   CREATE INDEX idx_training_forms_submitter ON training_forms(submitter);
   CREATE INDEX idx_training_forms_submission_date ON training_forms(submission_date);
   ```

2. **Monitor Resource Usage**:
   ```bash
   # Check system resources
   top
   htop
   iostat
   ```

3. **Optimize Database Queries**:
   ```python
   # Use pagination for large result sets
   def get_all_training_forms(page=1, per_page=10):
       offset = (page - 1) * per_page
       return query.offset(offset).limit(per_page).all()
   ```

4. **Enable Caching**:
   ```python
   # Cache lookup data
   @lru_cache(maxsize=128)
   def get_employee_list():
       return load_employees_from_csv()
   ```

### Memory Issues

#### Issue: High memory usage or memory leaks

**Symptoms**:
- Application memory usage grows over time
- Out of memory errors
- Server becomes unresponsive

**Resolution Steps**:

1. **Check Database Connections**:
   ```python
   # Ensure proper session management
   with db_session() as session:
       # Database operations
       pass  # Session automatically closed
   ```

2. **Monitor Memory Usage**:
   ```bash
   # Check memory usage
   free -h
   ps aux | grep python
   ```

3. **Profile Memory Usage**:
   ```python
   # Use memory profiler
   from memory_profiler import profile
   
   @profile
   def memory_intensive_function():
       # Function to profile
       pass
   ```

## Deployment Issues

### Production Deployment Problems

#### Issue: Application fails to start in production

**Symptoms**:
- Application works in development but not production
- Import errors or module not found
- Configuration issues

**Resolution Steps**:

1. **Check Environment Variables**:
   ```bash
   # Verify environment configuration
   echo $FLASK_ENV
   echo $DATABASE_URL
   echo $SECRET_KEY
   ```

2. **Verify Dependencies**:
   ```bash
   # Check installed packages
   pip list
   pip install -r requirements.txt
   ```

3. **Check File Permissions**:
   ```bash
   # Verify application file permissions
   ls -la *.py
   chmod +x main.py
   ```

4. **Review Production Configuration**:
   ```python
   # Production settings
   DEBUG = False
   USE_SQLITE = False
   DATABASE_URL = "mysql+pymysql://..."
   ```

### SSL/HTTPS Issues

#### Issue: HTTPS not working or certificate errors

**Symptoms**:
- SSL certificate warnings
- Mixed content errors
- HTTPS redirects not working

**Resolution Steps**:

1. **Check SSL Configuration**:
   ```python
   # Ensure secure cookie settings
   app.config['SESSION_COOKIE_SECURE'] = True
   app.config['SESSION_COOKIE_HTTPONLY'] = True
   ```

2. **Verify Certificate**:
   ```bash
   # Check SSL certificate
   openssl s_client -connect your-domain.com:443
   ```

3. **Update URLs**:
   ```python
   # Use HTTPS URLs in production
   if app.config.get('HTTPS_ENABLED'):
       url_scheme = 'https'
   ```

## Logging and Debugging

### Enable Debug Logging

```python
# Enhanced logging configuration
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')
```

### Common Log Locations

```bash
# Application logs
tail -f logs/app.log

# System logs
tail -f /var/log/syslog
tail -f /var/log/apache2/error.log
tail -f /var/log/nginx/error.log
```

### Debug Mode

```python
# Enable debug mode for development
app.run(debug=True, host='0.0.0.0', port=5000)
```

## Emergency Procedures

### Database Recovery

```bash
# Restore from backup
cp training_forms_backup.db training_forms.db

# Rebuild database from scratch
python setup_db.py --force-recreate
```

### Application Reset

```bash
# Stop application
pkill -f "python.*app.py"

# Clear cache and temporary files
rm -rf __pycache__/
rm -rf .pytest_cache/

# Restart application
python main.py
```

### File System Recovery

```bash
# Restore uploads from backup
rsync -av backup/uploads/ uploads/

# Fix file permissions
find uploads/ -type f -exec chmod 644 {} \;
find uploads/ -type d -exec chmod 755 {} \;
```

## Getting Help

### Contact Information

- **System Administrator**: Contact IT support
- **Development Team**: Create issue in project repository
- **Emergency Contact**: [Emergency contact information]

### Useful Commands

```bash
# Check application status
ps aux | grep python
netstat -tlnp | grep :5000

# View recent logs
tail -n 100 logs/app.log

# Check disk space
df -h

# Check memory usage
free -h

# Test database connection
python -c "from models import db_session; print('DB OK')"
```

### Documentation References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [WTForms Documentation](https://wtforms.readthedocs.io/)
- [LDAP3 Documentation](https://ldap3.readthedocs.io/) 
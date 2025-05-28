# File Management Documentation

## Overview

The Flask Survey Form System implements a comprehensive file management system for handling training-related attachments. The system provides secure file upload, storage, retrieval, and management capabilities with proper access controls and validation.

## File Management Architecture

### Components

1. **File Upload** (`utils.py`, `forms.py`): Secure file upload handling
2. **File Storage** (`uploads/` directory): Organized file storage system
3. **File Serving** (`app.py`): Secure file download and access control
4. **File Metadata** (`models.py`): Database tracking of file information
5. **File Validation** (`utils.py`, `forms.py`): Security and type validation

### File Processing Flow

```
File Upload → Validation → Secure Storage → Metadata Storage → Access Control → File Serving
```

## File Upload System

### Allowed File Types

The system supports a comprehensive set of file types for training documentation:

```python
ALLOWED_EXTENSIONS = {
    "pdf",      # Portable Document Format
    "doc",      # Microsoft Word (legacy)
    "docx",     # Microsoft Word (modern)
    "xls",      # Microsoft Excel (legacy)
    "xlsx",     # Microsoft Excel (modern)
    "jpg",      # JPEG images
    "jpeg",     # JPEG images
    "png",      # PNG images
    "csv",      # Comma-separated values
    "txt"       # Plain text files
}
```

### File Size Limits

```python
# Maximum file upload size: 32MB
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB
```

### File Validation

#### Extension Validation
```python
def allowed_file(filename):
    """Check if a filename has an allowed extension"""
    return (
        filename
        and "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )
```

#### Security Validation
- **Filename Sanitization**: Uses `secure_filename()` to prevent path traversal
- **File Type Verification**: Validates file extensions against allowed list
- **Size Limits**: Enforces maximum file size limits
- **Content Validation**: Basic file content validation

### Secure File Upload Process

#### 1. File Reception and Validation
```python
def save_file(file):
    """Save an uploaded file with a unique filename"""
    if not file or not file.filename or not allowed_file(file.filename):
        return None
    
    try:
        # Sanitize the filename
        filename = secure_filename(file.filename)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        
        # Construct file path
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save the file
        file.save(file_path)
        return unique_filename
        
    except Exception as e:
        logging.error(f"Error saving file: {e}")
        return None
```

#### 2. Multiple File Upload Handling
```python
# In form submission handler
uploaded_files = []
attachment_descriptions = []

# Process attachment descriptions
if form.attachment_descriptions.data:
    attachment_descriptions = [
        desc.strip() for desc in form.attachment_descriptions.data.split('\n')
        if desc.strip()
    ]

# Process file uploads
if form.attachments.data:
    for file in form.attachments.data:
        if file and file.filename:
            filename = save_file(file)
            if filename:
                uploaded_files.append(filename)
            else:
                flash(f"Failed to upload file: {file.filename}", "warning")
```

#### 3. File Metadata Storage
```python
# Save attachment metadata to database
for i, filename in enumerate(uploaded_files):
    description = (
        attachment_descriptions[i] 
        if i < len(attachment_descriptions) 
        else ""
    )
    
    attachment = Attachment(
        form_id=form_id,
        filename=filename,
        description=description
    )
    session.add(attachment)
```

## File Storage System

### Directory Structure

```
uploads/
├── form_10/           # Files for training form ID 10
│   ├── 20240115_143022_certificate.pdf
│   └── 20240115_143025_agenda.docx
├── form_11/           # Files for training form ID 11
│   ├── 20240116_091234_invoice.pdf
│   └── 20240116_091240_receipt.jpg
└── ...
```

### File Organization

#### Form-Based Organization
- Each training form gets its own subdirectory
- Directory named `form_{form_id}`
- All attachments for a form stored in its directory
- Enables easy cleanup and organization

#### Unique Filename Generation
```python
# Timestamp-based unique naming
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
unique_filename = f"{timestamp}_{secure_filename(original_filename)}"

# Example: 20240115_143022_training_certificate.pdf
```

### File Path Management

#### Upload Folder Configuration
```python
# Development configuration
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))

# Production configuration (network storage)
NETWORK_STORAGE_PATH = "\\\\strykercorp.com\\lim\\Engineering_DOG\\5. Automation & Controls\\01. Projects\\Training Form Invoices"
```

#### Dynamic Path Creation
```python
def get_form_upload_path(form_id):
    """Get the upload path for a specific form"""
    form_folder = f"form_{form_id}"
    upload_path = os.path.join(UPLOAD_FOLDER, form_folder)
    
    # Create directory if it doesn't exist
    os.makedirs(upload_path, exist_ok=True)
    
    return upload_path
```

## File Metadata Management

### Attachment Model

```python
class Attachment(Base):
    __tablename__ = "attachments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    form_id = Column(Integer, ForeignKey("training_forms.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    description = Column(String)
    
    # Relationship to training form
    training_form = relationship("TrainingForm", back_populates="attachments")
```

### Metadata Operations

#### Create Attachment Record
```python
def create_attachment(form_id, filename, description=""):
    """Create an attachment record in the database"""
    with db_session() as session:
        attachment = Attachment(
            form_id=form_id,
            filename=filename,
            description=description
        )
        session.add(attachment)
        session.flush()
        return attachment.id
```

#### Get Form Attachments
```python
def get_form_attachments(form_id):
    """Get all attachments for a training form"""
    with db_session() as session:
        attachments = session.query(Attachment).filter_by(form_id=form_id).all()
        return [
            {
                "id": att.id,
                "filename": att.filename,
                "description": att.description,
                "form_id": att.form_id
            }
            for att in attachments
        ]
```

#### Delete Attachment
```python
def delete_attachment(attachment_id):
    """Delete an attachment and its file"""
    with db_session() as session:
        attachment = session.query(Attachment).filter_by(id=attachment_id).first()
        if attachment:
            # Delete file from filesystem
            file_path = os.path.join(UPLOAD_FOLDER, f"form_{attachment.form_id}", attachment.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete database record
            session.delete(attachment)
            return True
        return False
```

## File Access Control

### Secure File Serving

```python
@app.route("/uploads/<path:filename>")
@login_required
def uploaded_file(filename):
    """Serve uploaded files with access control"""
    try:
        # Extract form ID from filename path
        if "/" in filename:
            form_folder, actual_filename = filename.split("/", 1)
            form_id = int(form_folder.replace("form_", ""))
        else:
            # Legacy support for files without form folders
            actual_filename = filename
            form_id = None
        
        # Check access permissions
        if form_id:
            form = get_training_form(form_id)
            if not can_access_form_files(current_user, form):
                abort(403)
        
        # Serve the file
        upload_path = os.path.join(UPLOAD_FOLDER, f"form_{form_id}") if form_id else UPLOAD_FOLDER
        return send_from_directory(upload_path, actual_filename)
        
    except (ValueError, FileNotFoundError):
        abort(404)
    except Exception as e:
        logging.error(f"Error serving file {filename}: {e}")
        abort(500)
```

### Access Control Rules

#### File Access Permissions
```python
def can_access_form_files(user, form):
    """Check if user can access files for a training form"""
    # Users can access files from their own forms
    if form.submitter == user.email:
        return True
    
    # Admins can access all files
    if is_admin_user(user):
        return True
    
    # Other users can access files from approved forms
    if form.approved:
        return True
    
    return False
```

#### Download Logging
```python
def log_file_download(user_email, filename, form_id):
    """Log file download for audit purposes"""
    logging.info(f"File download: {filename} by {user_email} for form {form_id}")
```

## File Upload in Forms

### Form Field Configuration

```python
# Multiple file upload field
attachments = MultipleFileField(
    "Attachments",
    validators=[DynamicRequiredIf("location_type", "Virtual")],
    description="Required for virtual training"
)

# File descriptions field
attachment_descriptions = TextAreaField(
    "Attachment Descriptions (one per line)",
    validators=[Optional()],
    description="Optional descriptions for each attachment"
)
```

### Frontend File Upload Interface

#### HTML Template
```html
<!-- File upload field -->
<div class="mb-3">
    {{ form.attachments.label(class="form-label") }}
    {{ form.attachments(class="form-control", multiple=True, accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.csv,.txt") }}
    <div class="form-text">
        Allowed file types: PDF, DOC, DOCX, XLS, XLSX, JPG, PNG, CSV, TXT (Max 32MB each)
    </div>
    {% if form.attachments.errors %}
        <div class="invalid-feedback d-block">
            {% for error in form.attachments.errors %}
                {{ error }}
            {% endfor %}
        </div>
    {% endif %}
</div>

<!-- File descriptions -->
<div class="mb-3">
    {{ form.attachment_descriptions.label(class="form-label") }}
    {{ form.attachment_descriptions(class="form-control", rows="3", placeholder="Enter description for each file (one per line)") }}
    <div class="form-text">
        Optional: Provide a description for each attachment (one per line)
    </div>
</div>
```

#### JavaScript File Handling
```javascript
// File upload preview and validation
document.getElementById('attachments').addEventListener('change', function(e) {
    const files = e.target.files;
    const maxSize = 32 * 1024 * 1024; // 32MB
    const allowedTypes = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'csv', 'txt'];
    
    for (let file of files) {
        // Check file size
        if (file.size > maxSize) {
            alert(`File ${file.name} is too large. Maximum size is 32MB.`);
            e.target.value = '';
            return;
        }
        
        // Check file type
        const extension = file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(extension)) {
            alert(`File type .${extension} is not allowed.`);
            e.target.value = '';
            return;
        }
    }
    
    // Update file count display
    updateFileCount(files.length);
});

function updateFileCount(count) {
    const countDisplay = document.getElementById('file-count');
    if (countDisplay) {
        countDisplay.textContent = `${count} file(s) selected`;
    }
}
```

## File Display and Management

### File List Display

#### Template for File Listing
```html
<!-- Display attachments in form view -->
{% if form.attachments %}
    <div class="mb-3">
        <h6>Attachments:</h6>
        <ul class="list-group">
            {% for attachment in form.attachments %}
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <strong>{{ attachment.filename.split('_', 1)[1] if '_' in attachment.filename else attachment.filename }}</strong>
                        {% if attachment.description %}
                            <br><small class="text-muted">{{ attachment.description }}</small>
                        {% endif %}
                    </div>
                    <div>
                        <a href="{{ url_for('uploaded_file', filename='form_' + form.id|string + '/' + attachment.filename) }}" 
                           class="btn btn-sm btn-outline-primary" target="_blank">
                            <i class="fas fa-download"></i> Download
                        </a>
                        {% if can_edit_form(current_user, form) %}
                            <button class="btn btn-sm btn-outline-danger ms-1" 
                                    onclick="deleteAttachment({{ attachment.id }})">
                                <i class="fas fa-trash"></i>
                            </button>
                        {% endif %}
                    </div>
                </li>
            {% endfor %}
        </ul>
    </div>
{% endif %}
```

#### File Management JavaScript
```javascript
function deleteAttachment(attachmentId) {
    if (confirm('Are you sure you want to delete this attachment?')) {
        fetch(`/api/attachments/${attachmentId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Error deleting attachment');
            }
        });
    }
}

function getCsrfToken() {
    return document.querySelector('meta[name=csrf-token]').getAttribute('content');
}
```

## File Cleanup and Maintenance

### Orphaned File Cleanup

```python
def cleanup_orphaned_files():
    """Remove files that no longer have database records"""
    with db_session() as session:
        # Get all attachment filenames from database
        db_files = set()
        attachments = session.query(Attachment).all()
        for att in attachments:
            db_files.add(f"form_{att.form_id}/{att.filename}")
        
        # Scan filesystem for files
        for form_dir in os.listdir(UPLOAD_FOLDER):
            if form_dir.startswith("form_"):
                form_path = os.path.join(UPLOAD_FOLDER, form_dir)
                if os.path.isdir(form_path):
                    for filename in os.listdir(form_path):
                        file_key = f"{form_dir}/{filename}"
                        if file_key not in db_files:
                            # Orphaned file - remove it
                            file_path = os.path.join(form_path, filename)
                            os.remove(file_path)
                            logging.info(f"Removed orphaned file: {file_path}")
```

### Form Deletion Cleanup

```python
def cleanup_form_files(form_id):
    """Remove all files associated with a deleted form"""
    form_folder = f"form_{form_id}"
    form_path = os.path.join(UPLOAD_FOLDER, form_folder)
    
    if os.path.exists(form_path):
        # Remove all files in the form directory
        for filename in os.listdir(form_path):
            file_path = os.path.join(form_path, filename)
            os.remove(file_path)
        
        # Remove the directory
        os.rmdir(form_path)
        logging.info(f"Cleaned up files for form {form_id}")
```

## File Export and Backup

### Export Functionality

#### Include Files in Export
```python
def export_form_with_attachments(form_id, export_path):
    """Export a form with all its attachments"""
    form = get_training_form(form_id)
    attachments = get_form_attachments(form_id)
    
    # Create export directory
    export_dir = os.path.join(export_path, f"form_{form_id}")
    os.makedirs(export_dir, exist_ok=True)
    
    # Copy form attachments
    for attachment in attachments:
        source_path = os.path.join(UPLOAD_FOLDER, f"form_{form_id}", attachment['filename'])
        dest_path = os.path.join(export_dir, attachment['filename'])
        
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
    
    # Create form metadata file
    metadata = {
        'form_id': form_id,
        'form_data': form.__dict__,
        'attachments': attachments,
        'export_date': datetime.now().isoformat()
    }
    
    with open(os.path.join(export_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
```

### Backup Strategies

#### Automated Backup
```python
def backup_files():
    """Create backup of all uploaded files"""
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_path = os.path.join("backups", backup_dir)
    
    # Copy entire uploads directory
    shutil.copytree(UPLOAD_FOLDER, backup_path)
    
    # Create backup manifest
    manifest = {
        'backup_date': datetime.now().isoformat(),
        'file_count': sum(len(files) for _, _, files in os.walk(backup_path)),
        'total_size': sum(os.path.getsize(os.path.join(dirpath, filename))
                         for dirpath, _, filenames in os.walk(backup_path)
                         for filename in filenames)
    }
    
    with open(os.path.join(backup_path, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)
    
    logging.info(f"Backup created: {backup_path}")
```

## Security Considerations

### File Security Measures

1. **Path Traversal Prevention**: Use `secure_filename()` for all uploads
2. **Type Validation**: Strict file type checking
3. **Size Limits**: Enforce maximum file sizes
4. **Access Control**: User-based file access permissions
5. **Virus Scanning**: Consider integration with antivirus scanning
6. **Content Validation**: Basic file content verification

### Production Security

#### Network Storage Security
```python
# Production file storage configuration
PRODUCTION_STORAGE = {
    'path': '\\\\strykercorp.com\\lim\\Engineering_DOG\\5. Automation & Controls\\01. Projects\\Training Form Invoices',
    'access_control': 'domain_based',
    'backup_enabled': True,
    'virus_scanning': True
}
```

#### File Encryption (Future Enhancement)
```python
def encrypt_file(file_path, key):
    """Encrypt uploaded files for additional security"""
    # Implementation for file encryption
    pass

def decrypt_file(encrypted_path, key):
    """Decrypt files for serving"""
    # Implementation for file decryption
    pass
```

## Performance Optimization

### File Serving Optimization

1. **Direct File Serving**: Use web server for static file serving in production
2. **Caching**: Implement file caching strategies
3. **Compression**: Compress files for faster transfer
4. **CDN Integration**: Use CDN for file distribution

### Storage Optimization

1. **File Deduplication**: Identify and remove duplicate files
2. **Compression**: Compress stored files to save space
3. **Archival**: Move old files to archival storage
4. **Cleanup**: Regular cleanup of orphaned files 
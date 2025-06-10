# File Management Documentation

## Overview

The Flask Survey Form System implements a comprehensive file management system for handling training-related attachments, application logs, and database backups. The system provides secure file upload, storage, retrieval, and management capabilities with proper access controls and validation. All data is centrally organized using a configurable `DATA_FOLDER` structure with files organized by form ID for better organization and security.

## File Management Architecture

### Components

1. **File Upload** (`utils.py`, `forms.py`): Secure file upload handling with form-specific organization
2. **Data Storage** (`DATA_FOLDER` structure): Centralized data storage including uploads, logs, and backups
3. **File Serving** (`app.py`): Secure file download and access control
4. **File Metadata** (`models.py`): Database tracking of file information with descriptions
5. **File Validation** (`utils.py`, `forms.py`): Security and type validation
6. **Logging System** (`logging_config.py`): Centralized application logging with environment-specific paths
7. **Backup System** (`scripts/maintenance.py`): Automated database backup with organized storage
8. **Employee Data Management** (`attached_assets/`): Automated employee directory CSV file synchronization

### File Processing Flow

```
File Upload → Validation → Form-Specific Storage → Metadata Storage → Access Control → File Serving
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
def save_file(file, form_id):
    """Save an uploaded file with form-specific organization"""
    if not file or not file.filename or not allowed_file(file.filename):
        return None
    
    try:
        # Sanitize the filename
        filename = secure_filename(file.filename)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        
        # Create form-specific directory
        form_upload_path = get_form_upload_path(form_id)
        
        # Construct file path
        file_path = os.path.join(form_upload_path, unique_filename)
        
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
            filename = save_file(file, form_id)
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
# Production: C:/TrainingAppData/
# Development: project_root/TrainingAppData/

DATA_FOLDER/
├── Uploads/                         # File attachments organized by form
│   ├── form_10/                     # Files for training form ID 10
│   │   ├── 20240115_143022_certificate.pdf
│   │   └── 20240115_143025_agenda.docx
│   ├── form_11/                     # Files for training form ID 11
│   │   ├── 20240116_091234_invoice.pdf
│   │   └── 20240116_091240_receipt.jpg
│   ├── form_12/                     # Files for training form ID 12
│   │   ├── 20240117_101520_training_materials.zip
│   │   ├── 20240117_101525_course_outline.pdf
│   │   └── 20240117_101530_completion_cert.pdf
│   └── ...
├── Logs/                           # Application logs
│   ├── app.log                     # Current log file
│   ├── app.log.1                   # Rotated log files
│   └── app.log.2
└── Backups/                        # Database backups
    ├── backup_20240115_143022.sql
    ├── backup_20240116_091234.sql
    └── ...

attached_assets/                     # Static reference files (project directory)
├── EmployeeListFirstLastDept.csv    # Employee directory (updated nightly)
├── limerick IDA .xlsx               # Reference documents
└── Claim-Form-5-Training new GBER Rules.xlsx
```

### File Organization

#### Form-Based Organization
- Each training form gets its own subdirectory
- Directory named `form_{form_id}`
- All attachments for a form stored in its directory
- Enables easy cleanup and organization
- Improves security by isolating form files

#### Unique Filename Generation
```python
# Timestamp-based unique naming
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
unique_filename = f"{timestamp}_{secure_filename(original_filename)}"

# Example: 20240115_143022_training_certificate.pdf
```

### File Path Management

#### Centralized Data Folder Configuration

The application uses a centralized `DATA_FOLDER` configuration to manage all data storage including uploads, logs, and backups. This approach prevents deployment issues and provides consistent data organization.

**Problem Solved**: Previously, when deploying to production, the local development folders would overwrite production data folders, causing uploaded attachments and logs to be lost.

**Solution Implemented**: Centralized data folder configuration with environment-specific storage outside the project directory.

```python
# Centralized data folder configuration (config.py)
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')

# Set folder to save data to (currently only used for attachments, logs, backups)
DATA_FOLDER = os.environ.get("DATA_FOLDER", "C:/TrainingAppData") if FLASK_ENV == 'production' else os.path.abspath(os.path.join(os.path.dirname(__file__), "TrainingAppData"))

# Usage in app.py
upload_folder = app.config["DATA_FOLDER"] + "/Uploads"
```

**Environment-specific data organization**:
```
# Production (C:/TrainingAppData/)
C:/TrainingAppData/
├── Uploads/          # File attachments
│   ├── form_10/
│   ├── form_11/
│   └── ...
├── Logs/            # Application logs
│   ├── app.log
│   └── app.log.1
└── Backups/         # Database backups
    ├── backup_20240115_143022.sql
    └── ...

# Development (project/TrainingAppData/)
TrainingAppData/
├── Uploads/
├── Logs/
└── Backups/
```

**Key Benefits**:
1. **Deployment Safety**: Production deployments can't overwrite data folders
2. **Environment Isolation**: Each environment has its own data storage
3. **Data Persistence**: Production data is preserved outside the project directory
4. **Centralized Management**: All data types (uploads, logs, backups) in one location
5. **Git Compatibility**: Local `TrainingAppData/` folder can be gitignored
6. **Simplified Configuration**: Single `DATA_FOLDER` variable controls all data storage

**Configuration Variables**:
- **`DATA_FOLDER`**: Root directory for all application data
  - **Production**: `C:/TrainingAppData` (default) or custom path via environment variable
  - **Development**: `project_root/TrainingAppData` (local folder)

**Migration Notes**: Existing production files should be moved to `C:/TrainingAppData/` structure before deployment. The production deployment will automatically create the new folder structure if it doesn't exist.

**Legacy Network Storage Configuration**:
```python
# Production network storage (if using network shares)
NETWORK_STORAGE_PATH = "\\\\strykercorp.com\\lim\\Engineering_DOG\\5. Automation & Controls\\01. Projects\\Training Form Invoices"
```

#### Dynamic Path Creation
```python
def get_form_upload_path(form_id):
    """Get the upload path for a specific form"""
    from config import DATA_FOLDER
    form_folder = f"form_{form_id}"
    upload_folder = os.path.join(DATA_FOLDER, "Uploads")
    upload_path = os.path.join(upload_folder, form_folder)
    
    # Create directory if it doesn't exist
    os.makedirs(upload_path, exist_ok=True)
    
    return upload_path
```

## File Metadata Management

### Enhanced Attachment Model

```python
class Attachment(Base):
    __tablename__ = "attachments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    form_id = Column(Integer, ForeignKey("training_forms.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    description = Column(String)
    
    # Relationship to training form
    training_form = relationship("TrainingForm", back_populates="attachments")
    
    def to_dict(self):
        """Convert attachment to dictionary"""
        return {
            "id": self.id,
            "form_id": self.form_id,
            "filename": self.filename,
            "description": self.description,
            "display_name": self.get_display_name(),
            "file_size": self.get_file_size(),
            "upload_date": self.get_upload_date()
        }
    
    def get_display_name(self):
        """Get user-friendly filename"""
        # Remove timestamp prefix for display
        if '_' in self.filename:
            return '_'.join(self.filename.split('_')[1:])
        return self.filename
    
    def get_file_size(self):
        """Get file size in human-readable format"""
        try:
            from config import DATA_FOLDER
            upload_folder = os.path.join(DATA_FOLDER, "Uploads")
            file_path = os.path.join(upload_folder, f"form_{self.form_id}", self.filename)
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                return format_file_size(size)
        except Exception:
            pass
        return "Unknown"
    
    def get_upload_date(self):
        """Extract upload date from filename"""
        try:
            if '_' in self.filename:
                timestamp_str = self.filename.split('_')[0]
                return datetime.strptime(timestamp_str, "%Y%m%d").strftime("%Y-%m-%d")
        except Exception:
            pass
        return "Unknown"
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
        return [attachment.to_dict() for attachment in attachments]
```

#### Delete Attachment
```python
def delete_attachment(attachment_id):
    """Delete an attachment and its file"""
    with db_session() as session:
        attachment = session.query(Attachment).filter_by(id=attachment_id).first()
        if attachment:
            # Delete file from filesystem
            from config import DATA_FOLDER
            upload_folder = os.path.join(DATA_FOLDER, "Uploads")
            file_path = os.path.join(upload_folder, f"form_{attachment.form_id}", attachment.filename)
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
        from config import DATA_FOLDER
        base_upload_folder = os.path.join(DATA_FOLDER, "Uploads")
        upload_path = os.path.join(base_upload_folder, f"form_{form_id}") if form_id else base_upload_folder
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

### Enhanced Form Field Configuration

```python
# Multiple file upload field with virtual training requirement
attachments = MultipleFileField(
    "Attachments",
    validators=[RequiredAttachmentsIfVirtual("At least one attachment is required for virtual training.")],
    description="Required for virtual training"
)

# Enhanced file descriptions field
attachment_descriptions = TextAreaField(
    "Attachment Descriptions (one per line)",
    validators=[Optional()],
    description="Optional descriptions for each attachment (one per line)"
)
```

### Frontend File Upload Interface

#### Enhanced HTML Template
```html
<!-- File upload field with enhanced features -->
<div class="mb-3">
    {{ form.attachments.label(class="form-label") }}
    {{ form.attachments(class="form-control", multiple=True, 
        accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.csv,.txt",
        **{"data-max-files": "10", "data-max-size": "33554432"}) }}
    <div class="form-text">
        Allowed file types: PDF, DOC, DOCX, XLS, XLSX, JPG, PNG, CSV, TXT (Max 32MB each, 10 files max)
    </div>
    <div id="file-upload-preview" class="mt-2"></div>
    {% if form.attachments.errors %}
        <div class="invalid-feedback d-block">
            {% for error in form.attachments.errors %}
                {{ error }}
            {% endfor %}
        </div>
    {% endif %}
</div>

<!-- Enhanced file descriptions -->
<div class="mb-3">
    {{ form.attachment_descriptions.label(class="form-label") }}
    {{ form.attachment_descriptions(class="form-control", rows="3", 
        placeholder="Enter description for each file (one per line)") }}
    <div class="form-text">
        Optional: Provide a description for each attachment (one per line)
    </div>
</div>
```

#### Enhanced JavaScript File Handling
```javascript
// Enhanced file upload preview and validation
document.getElementById('attachments').addEventListener('change', function(e) {
    const files = e.target.files;
    const maxSize = 32 * 1024 * 1024; // 32MB
    const maxFiles = 10;
    const allowedTypes = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'csv', 'txt'];
    
    // Check file count
    if (files.length > maxFiles) {
        alert(`Too many files selected. Maximum is ${maxFiles} files.`);
        e.target.value = '';
        return;
    }
    
    let totalSize = 0;
    const fileList = [];
    
    for (let file of files) {
        // Check file size
        if (file.size > maxSize) {
            alert(`File ${file.name} is too large. Maximum size is 32MB.`);
            e.target.value = '';
            return;
        }
        
        totalSize += file.size;
        
        // Check file type
        const extension = file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(extension)) {
            alert(`File type .${extension} is not allowed.`);
            e.target.value = '';
            return;
        }
        
        fileList.push({
            name: file.name,
            size: formatFileSize(file.size),
            type: extension.toUpperCase()
        });
    }
    
    // Update file preview
    updateFilePreview(fileList, totalSize);
});

function updateFilePreview(files, totalSize) {
    const preview = document.getElementById('file-upload-preview');
    if (files.length === 0) {
        preview.innerHTML = '';
        return;
    }
    
    let html = '<div class="card mt-2"><div class="card-body p-2">';
    html += '<h6 class="mb-2">Selected Files:</h6>';
    html += '<div class="row g-2">';
    
    files.forEach((file, index) => {
        html += `
            <div class="col-md-6">
                <div class="d-flex align-items-center">
                    <i class="bi bi-file-earmark-text me-2"></i>
                    <div class="flex-grow-1">
                        <div class="small fw-bold">${file.name}</div>
                        <div class="text-muted" style="font-size: 0.75rem;">${file.type} - ${file.size}</div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    html += `<div class="mt-2 text-muted small">Total: ${files.length} files (${formatFileSize(totalSize)})</div>`;
    html += '</div></div>';
    
    preview.innerHTML = html;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
```

## File Display and Management

### Enhanced File List Display

#### Template for File Listing
```html
<!-- Enhanced display attachments in form view -->
{% if attachments %}
    <div class="mb-3">
        <h6>Attachments ({{ attachments|length }}):</h6>
        <div class="row g-2">
            {% for attachment in attachments %}
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-body p-3">
                            <div class="d-flex align-items-start">
                                <div class="file-icon me-2">
                                    <i class="bi bi-file-earmark-{{ get_file_icon(attachment.filename) }} fs-4 text-primary"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <div class="fw-bold">{{ attachment.display_name }}</div>
                                    {% if attachment.description %}
                                        <div class="text-muted small mb-1">{{ attachment.description }}</div>
                                    {% endif %}
                                    <div class="text-muted" style="font-size: 0.75rem;">
                                        {{ attachment.file_size }} • {{ attachment.upload_date }}
                                    </div>
                                </div>
                            </div>
                            <div class="mt-2">
                                <a href="{{ url_for('uploaded_file', filename='form_' + form.id|string + '/' + attachment.filename) }}" 
                                   class="btn btn-sm btn-outline-primary" target="_blank">
                                    <i class="bi bi-download"></i> Download
                                </a>
                                {% if can_edit_form(current_user, form) %}
                                    <button class="btn btn-sm btn-outline-danger ms-1" 
                                            onclick="deleteAttachment({{ attachment.id }})">
                                        <i class="bi bi-trash"></i> Delete
                                    </button>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>
    </div>
{% else %}
    <div class="text-muted">No attachments</div>
{% endif %}
```

#### Enhanced File Management JavaScript
```javascript
function deleteAttachment(attachmentId) {
    if (confirm('Are you sure you want to delete this attachment?')) {
        fetch(`/api/attachments/${attachmentId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                return response.json().then(data => {
                    throw new Error(data.error || 'Error deleting attachment');
                });
            }
        })
        .catch(error => {
            alert('Error deleting attachment: ' + error.message);
        });
    }
}

function getCsrfToken() {
    return document.querySelector('meta[name=csrf-token]').getAttribute('content');
}

function getFileIcon(filename) {
    const extension = filename.split('.').pop().toLowerCase();
    const iconMap = {
        'pdf': 'pdf',
        'doc': 'word',
        'docx': 'word',
        'xls': 'excel',
        'xlsx': 'excel',
        'jpg': 'image',
        'jpeg': 'image',
        'png': 'image',
        'csv': 'csv',
        'txt': 'text'
    };
    return iconMap[extension] || 'text';
}
```

## File Cleanup and Maintenance

### Enhanced Orphaned File Cleanup

```python
def cleanup_orphaned_files():
    """Remove files that no longer have database records"""
    from config import DATA_FOLDER
    upload_folder = os.path.join(DATA_FOLDER, "Uploads")
    
    with db_session() as session:
        # Get all attachment filenames from database
        db_files = set()
        attachments = session.query(Attachment).all()
        for att in attachments:
            db_files.add(f"form_{att.form_id}/{att.filename}")
        
        # Scan filesystem for files
        orphaned_count = 0
        for form_dir in os.listdir(upload_folder):
            if form_dir.startswith("form_"):
                form_path = os.path.join(upload_folder, form_dir)
                if os.path.isdir(form_path):
                    for filename in os.listdir(form_path):
                        file_key = f"{form_dir}/{filename}"
                        if file_key not in db_files:
                            # Orphaned file - remove it
                            file_path = os.path.join(form_path, filename)
                            try:
                                os.remove(file_path)
                                orphaned_count += 1
                                logging.info(f"Removed orphaned file: {file_path}")
                            except Exception as e:
                                logging.error(f"Failed to remove orphaned file {file_path}: {e}")
        
        logging.info(f"Cleanup completed: {orphaned_count} orphaned files removed")
        return orphaned_count
```

### Form Deletion Cleanup

```python
def cleanup_form_files(form_id):
    """Remove all files associated with a deleted form"""
    from config import DATA_FOLDER
    upload_folder = os.path.join(DATA_FOLDER, "Uploads")
    form_folder = f"form_{form_id}"
    form_path = os.path.join(upload_folder, form_folder)
    
    if os.path.exists(form_path):
        try:
            # Remove all files in the form directory
            file_count = 0
            for filename in os.listdir(form_path):
                file_path = os.path.join(form_path, filename)
                os.remove(file_path)
                file_count += 1
            
            # Remove the directory
            os.rmdir(form_path)
            logging.info(f"Cleaned up files for form {form_id}: {file_count} files removed")
            return file_count
        except Exception as e:
            logging.error(f"Error cleaning up files for form {form_id}: {e}")
            return 0
    return 0
```

## File Export and Backup

### Enhanced Export Functionality

#### Include Files in Export
```python
def export_form_with_attachments(form_id, export_path):
    """Export a form with all its attachments"""
    from config import DATA_FOLDER
    upload_folder = os.path.join(DATA_FOLDER, "Uploads")
    
    form = get_training_form(form_id)
    attachments = get_form_attachments(form_id)
    
    # Create export directory
    export_dir = os.path.join(export_path, f"form_{form_id}_export")
    os.makedirs(export_dir, exist_ok=True)
    
    # Copy form attachments
    copied_files = []
    for attachment in attachments:
        source_path = os.path.join(upload_folder, f"form_{form_id}", attachment['filename'])
        dest_filename = attachment['display_name']
        dest_path = os.path.join(export_dir, dest_filename)
        
        if os.path.exists(source_path):
            try:
                shutil.copy2(source_path, dest_path)
                copied_files.append({
                    'original': attachment['filename'],
                    'exported': dest_filename,
                    'description': attachment['description']
                })
            except Exception as e:
                logging.error(f"Failed to copy {source_path} to {dest_path}: {e}")
    
    # Create enhanced form metadata file
    metadata = {
        'form_id': form_id,
        'form_data': form,
        'attachments': copied_files,
        'export_date': datetime.now().isoformat(),
        'export_version': '2.0'
    }
    
    with open(os.path.join(export_dir, 'form_metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    logging.info(f"Form {form_id} exported to {export_dir} with {len(copied_files)} attachments")
    return export_dir, len(copied_files)
```

### Enhanced Backup Strategies

#### Automated Backup with Metadata
```python
def backup_files_with_metadata():
    """Create comprehensive backup of all uploaded files with metadata"""
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    # Use DATA_FOLDER configuration for consistent backup location
    from config import DATA_FOLDER
    backup_path = os.path.join(DATA_FOLDER, "Backups", backup_dir)
    
    # Create backup directory structure
    os.makedirs(backup_path, exist_ok=True)
    
    # Copy entire uploads directory
    uploads_backup = os.path.join(backup_path, "uploads")
    upload_folder = os.path.join(DATA_FOLDER, "Uploads")
    shutil.copytree(upload_folder, uploads_backup)
    
    # Copy attached assets (including employee directory)
    assets_backup = os.path.join(backup_path, "attached_assets")
    shutil.copytree("attached_assets", assets_backup)
    
    # Create comprehensive backup manifest
    manifest = {
        'backup_date': datetime.now().isoformat(),
        'backup_version': '2.0',
        'total_forms': 0,
        'total_files': 0,
        'total_size': 0,
        'employee_data_included': True,
        'forms': []
    }
    
    # Analyze each form's files
    for form_dir in os.listdir(uploads_backup):
        if form_dir.startswith("form_"):
            form_id = int(form_dir.replace("form_", ""))
            form_path = os.path.join(uploads_backup, form_dir)
            
            if os.path.isdir(form_path):
                form_info = {
                    'form_id': form_id,
                    'files': [],
                    'file_count': 0,
                    'total_size': 0
                }
                
                for filename in os.listdir(form_path):
                    file_path = os.path.join(form_path, filename)
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        form_info['files'].append({
                            'filename': filename,
                            'size': file_size,
                            'display_name': filename.split('_', 1)[1] if '_' in filename else filename
                        })
                        form_info['file_count'] += 1
                        form_info['total_size'] += file_size
                
                manifest['forms'].append(form_info)
                manifest['total_forms'] += 1
                manifest['total_files'] += form_info['file_count']
                manifest['total_size'] += form_info['total_size']
    
    # Save manifest
    with open(os.path.join(backup_path, 'backup_manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)
    
    logging.info(f"Comprehensive backup created: {backup_path}")
    logging.info(f"Backup contains {manifest['total_forms']} forms, {manifest['total_files']} files, {format_file_size(manifest['total_size'])}")
    
    return backup_path, manifest
```

## Security Considerations

### Enhanced File Security Measures

1. **Path Traversal Prevention**: Use `secure_filename()` for all uploads
2. **Type Validation**: Strict file type checking with extension verification
3. **Size Limits**: Enforce maximum file sizes per file and total upload
4. **Access Control**: Enhanced user-based file access permissions
5. **Virus Scanning**: Consider integration with antivirus scanning
6. **Content Validation**: Basic file content verification
7. **Form Isolation**: Files isolated by form ID for security

### Production Security

#### Network Storage Security
```python
# Enhanced production file storage configuration
PRODUCTION_STORAGE = {
    'path': '\\\\strykercorp.com\\lim\\Engineering_DOG\\5. Automation & Controls\\01. Projects\\Training Form Invoices',
    'access_control': 'domain_based',
    'backup_enabled': True,
    'virus_scanning': True,
    'encryption': 'at_rest',
    'audit_logging': True
}
```

#### File Encryption (Future Enhancement)
```python
def encrypt_file(file_path, key):
    """Encrypt uploaded files for additional security"""
    # Implementation for file encryption at rest
    pass

def decrypt_file(encrypted_path, key):
    """Decrypt files for serving"""
    # Implementation for file decryption on access
    pass
```

## Performance Optimization

### File Serving Optimization

1. **Direct File Serving**: Use web server for static file serving in production
2. **Caching**: Implement file metadata caching strategies
3. **Compression**: Compress files for faster transfer
4. **CDN Integration**: Use CDN for file distribution
5. **Lazy Loading**: Load file lists progressively

### Storage Optimization

1. **File Deduplication**: Identify and remove duplicate files across forms
2. **Compression**: Compress stored files to save space
3. **Archival**: Move old files to archival storage
4. **Cleanup Automation**: Regular cleanup of orphaned files
5. **Storage Monitoring**: Track storage usage and growth patterns 
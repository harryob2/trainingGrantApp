# Upload Folder Configuration Changes

## Overview
Updated the application to use environment-specific upload folders to prevent deployment issues where production deployments would overwrite uploaded files.

## Problem Solved
Previously, when deploying to production, the local development `uploads/` folder (which is empty in development) would overwrite the production uploads folder, causing all uploaded attachments to be lost.

## Solution Implemented

### Environment-Specific Upload Folders
- **Development**: `uploads/` (local folder within project directory)
- **Staging**: `uploads_staging/` (local folder for testing)  
- **Production**: `c:/TrainingAppFormUploads/` (dedicated folder outside project directory)

### Configuration Changes

#### `config.py`
```python
# Set upload folder based on environment
if FLASK_ENV == 'production':
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "c:/TrainingAppFormUploads")
else:
    # Development and staging use local uploads folder
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads")))
```

#### `.github/workflows/deploy.yml`
- Production deployment now sets `UPLOAD_FOLDER=c:/TrainingAppFormUploads`
- Added step to create production uploads directory if it doesn't exist

#### `env.example`
- Added comments documenting the environment-specific behavior
- Shows both development and production examples

## Key Benefits

1. **Deployment Safety**: Production deployments can't overwrite uploaded files
2. **Environment Isolation**: Each environment has its own upload storage
3. **Data Persistence**: Production files are preserved outside the project directory
4. **Clean Development**: Local development files don't interfere with deployments
5. **Git Compatibility**: `uploads/` folder remains in `.gitignore` as intended

## File Organization
Files are still organized by form ID within each environment's upload folder:
```
c:/TrainingAppFormUploads/     (Production)
├── form_10/
│   ├── 20240115_143022_certificate.pdf
│   └── 20240115_143025_agenda.docx
├── form_11/
│   └── 20240116_091234_invoice.pdf
└── ...

uploads/                       (Development)
├── form_1/
└── form_2/
```

## Migration Notes
- Existing production files should be moved to `c:/TrainingAppFormUploads/` before deployment
- The production deployment will automatically create the new folder if it doesn't exist
- No code changes needed for file access - the application automatically uses the correct path

## Implementation Status
✅ **Complete** - All changes have been implemented and tested:
- Configuration updated for environment-specific paths
- Deployment pipeline updated to use correct production path
- Documentation updated across all relevant files
- Enhanced error handling and logging added

## Files Modified
1. `config.py` - Environment-specific upload folder logic
2. `.github/workflows/deploy.yml` - Production deployment configuration
3. `env.example` - Documentation of environment variables
4. `app.py` - Enhanced upload folder creation and logging
5. `utils.py` - Improved upload folder handling
6. Documentation files updated with new configuration details 
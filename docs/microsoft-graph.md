# Microsoft Graph API Integration

## Overview

The `microsoft_graph.py` module provides a centralized interface for interacting with Microsoft Graph API services. This module consolidates all Microsoft Graph functionality used throughout the Training Form Application, including employee data synchronization and user profile picture retrieval.

## Architecture

### MicrosoftGraphClient Class

The core `MicrosoftGraphClient` class handles authentication, token management, and API calls to Microsoft Graph endpoints.

```python
from microsoft_graph import MicrosoftGraphClient

# Initialize client (uses environment variables for credentials)
client = MicrosoftGraphClient()

# Or provide credentials explicitly
client = MicrosoftGraphClient(
    client_id="your-client-id",
    client_secret="your-client-secret", 
    tenant_id="your-tenant-id"
)
```

### Key Features

- **Automatic Token Management**: Handles OAuth2 authentication and token refresh
- **Error Handling**: Comprehensive error handling with logging
- **Performance Optimization**: Token caching to minimize authentication requests
- **Modular Design**: Clean separation of concerns for different Graph API operations

## Configuration

### Required Environment Variables

```bash
# Azure App Registration credentials
AZURE_CLIENT_ID=your-azure-app-client-id
AZURE_CLIENT_SECRET=your-azure-app-client-secret
AZURE_TENANT_ID=your-azure-tenant-id
```

### Azure App Registration Setup

1. **Create App Registration** in Azure Portal
2. **API Permissions**: Grant the following Microsoft Graph permissions:
   - `User.Read.All` (Application permission)
   - `Directory.Read.All` (Application permission)
3. **Client Secret**: Generate and securely store client secret
4. **Admin Consent**: Grant admin consent for application permissions

## API Methods

### Employee Data Management

#### `get_all_employees(site_filter, domain_filter)`

Retrieves filtered employee list from Microsoft Graph.

**Parameters:**
- `site_filter` (str): Office location filter (default: "Limerick, Limerick Raheen Business Park")
- `domain_filter` (str): Email domain filter (default: "@stryker.com")

**Returns:** List of employee dictionaries with keys: `first_name`, `last_name`, `email`, `department`

**Example:**
```python
employees = client.get_all_employees()
for emp in employees:
    print(f"{emp['first_name']} {emp['last_name']} - {emp['department']}")
```

### User Profile Management

#### `get_user_profile_picture(email)`

Retrieves user's profile picture as base64 data URL.

**Parameters:**
- `email` (str): User's email address

**Returns:** Base64 data URL string or None if not found

**Example:**
```python
profile_pic = client.get_user_profile_picture("user@stryker.com")
if profile_pic:
    # profile_pic is a data URL like "data:image/jpeg;base64,..."
    print(f"Profile picture size: {len(profile_pic)} characters")
```

#### `get_user_info(email)`

Retrieves basic user information from Microsoft Graph.

**Parameters:**
- `email` (str): User's email address

**Returns:** Dictionary with user information or None if not found

**Example:**
```python
user_info = client.get_user_info("user@stryker.com")
if user_info:
    print(f"Display name: {user_info['display_name']}")
    print(f"Department: {user_info['department']}")
```

## Convenience Functions

For backward compatibility and simple usage, the module provides standalone functions:

```python
from microsoft_graph import get_all_employees, get_user_profile_picture, get_user_info

# Simple function calls
employees = get_all_employees()
profile_pic = get_user_profile_picture("user@stryker.com")
user_info = get_user_info("user@stryker.com")
```

## Authentication Flow

### OAuth2 Client Credentials Flow

The module uses OAuth2 client credentials flow for secure API access:

1. **Token Request**: Authenticate with Azure using client credentials
2. **Token Caching**: Store access token with automatic expiry tracking
3. **Token Refresh**: Automatically refresh tokens 1 minute before expiry
4. **API Calls**: Include Bearer token in all Graph API requests

### Token Management

```python
# Token is automatically managed internally
client = MicrosoftGraphClient()

# First call acquires token
employees = client.get_all_employees()

# Subsequent calls reuse cached token
profile_pic = client.get_user_profile_picture("user@stryker.com")

# Token automatically refreshes when needed
```

## Error Handling

### API Error Categories

1. **Authentication Errors**
   - Invalid credentials
   - Token acquisition failures
   - Permission denied

2. **User/Resource Errors**
   - User not found (404)
   - Resource not available
   - No profile picture set

3. **Network Errors**
   - Connection timeouts
   - Service unavailable
   - Rate limiting

### Error Response Strategy

All methods handle errors gracefully:

```python
try:
    profile_pic = get_user_profile_picture("user@stryker.com")
    if profile_pic:
        # Use profile picture
        pass
    else:
        # User has no profile picture - use default
        pass
except Exception as e:
    # Network or API error - use default
    logger.error(f"Failed to get profile picture: {e}")
```

### Logging

All operations are logged with appropriate levels:

```python
# Successful operations
logger.info("Successfully acquired access token")
logger.info(f"Profile picture retrieved for user: {email}")

# Warning conditions
logger.warning(f"No profile picture found for user: {email}")

# Error conditions
logger.error(f"Failed to fetch profile picture for {email}: {error}")
```

## Performance Considerations

### Token Caching

- Access tokens cached in memory for their lifetime (typically 1 hour)
- Automatic refresh 1 minute before expiry prevents API delays
- No persistent token storage for security

### API Call Optimization

- Minimal required permissions to reduce security surface
- Efficient filtering to reduce data transfer
- Pagination support for large employee lists
- Timeout configuration to prevent hanging requests

### Memory Usage

- Profile pictures returned as base64 data URLs (5-50KB typical)
- Employee lists cached at application level, not module level
- No persistent storage of sensitive data

## Integration Points

### Maintenance Scripts

The `scripts/maintenance.py` file uses this module for employee data synchronization:

```python
from microsoft_graph import get_all_employees

# Replace complex inline Graph API code with simple function call
employees_data = get_all_employees()
```

### Authentication System

The `auth.py` module uses this for profile picture retrieval during login:

```python
from microsoft_graph import get_user_profile_picture

# Fetch profile picture during login process
profile_picture = get_user_profile_picture(user_data['email'])
if profile_picture:
    session['user_profile_picture'] = profile_picture
```

## Security Considerations

### Credential Management

- Environment variables for secure credential storage
- No hardcoded credentials in source code
- Client secret rotation supported without code changes

### Data Privacy

- No persistent storage of user profile data
- Profile pictures cached only in user sessions
- Minimal data retention in accordance with privacy policies

### API Security

- Least privilege principle for API permissions
- Secure OAuth2 authentication flow
- Automatic token expiry and refresh

## Testing

### Test Script

Use the provided test script to verify functionality:

```bash
python test_profile_pictures.py
```

### Test Coverage

- Microsoft Graph API connectivity
- Authentication and token management
- Employee data retrieval
- Profile picture functionality
- Error handling scenarios

### Manual Testing

```python
# Test basic connectivity
from microsoft_graph import MicrosoftGraphClient
client = MicrosoftGraphClient()
token = client._get_access_token()
print("Connected!" if token else "Connection failed")

# Test employee data
employees = client.get_all_employees()
print(f"Found {len(employees)} employees")

# Test profile picture
profile_pic = client.get_user_profile_picture("test@stryker.com")
print("Profile picture found" if profile_pic else "No profile picture")
```

## Troubleshooting

### Common Issues

#### Authentication Failures
- Verify Azure credentials in environment variables
- Check API permissions and admin consent
- Verify network connectivity to Microsoft Graph

#### No Data Returned
- Check user exists in Azure AD
- Verify filtering criteria (site, domain)
- Review application logs for detailed errors

#### Performance Issues
- Monitor token refresh frequency
- Check API rate limiting
- Verify network latency to Microsoft Graph

### Debug Commands

```bash
# Test connectivity
python -c "from microsoft_graph import MicrosoftGraphClient; print('OK' if MicrosoftGraphClient()._get_access_token() else 'FAIL')"

# Check environment
env | grep AZURE

# Run full test suite
python test_profile_pictures.py
```

## Migration Notes

### From Inline Implementation

Previous implementation in `maintenance.py` contained inline Microsoft Graph code. This has been migrated to use the new module:

**Before:**
```python
# Complex token acquisition and API calls directly in maintenance.py
token_response = requests.post(token_url, data=token_data)
# ... 100+ lines of Graph API code
```

**After:**
```python
# Simple function call
from microsoft_graph import get_all_employees
employees_data = get_all_employees()
```

### Benefits of Migration

- **Code Reuse**: Same Graph API client used across application
- **Maintainability**: Single location for Graph API logic
- **Testing**: Isolated module enables better testing
- **Error Handling**: Consistent error handling patterns
- **Performance**: Optimized token management and caching 
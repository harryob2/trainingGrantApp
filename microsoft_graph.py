"""
Microsoft Graph API integration for the Training Form Application

This module provides functions for interacting with Microsoft Graph API:
- Employee data synchronization
- User profile picture retrieval
- Authentication and token management
"""

import os
import logging
import requests
import base64
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class MicrosoftGraphClient:
    """Microsoft Graph API client for employee data and profile pictures"""
    
    def __init__(self, client_id: str = None, client_secret: str = None, tenant_id: str = None):
        """Initialize the Microsoft Graph client with Azure credentials"""
        self.client_id = client_id or os.environ.get('AZURE_CLIENT_ID')
        self.client_secret = client_secret or os.environ.get('AZURE_CLIENT_SECRET')
        self.tenant_id = tenant_id or os.environ.get('AZURE_TENANT_ID')
        
        if not all([self.client_id, self.client_secret, self.tenant_id]):
            raise ValueError("Missing Azure credentials. Set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID environment variables.")
        
        self._access_token = None
        self._token_expires_at = None
    
    def _get_access_token(self) -> str:
        """Get access token using client credentials flow"""
        # Check if we have a valid token
        if self._access_token and self._token_expires_at:
            import time
            if time.time() < self._token_expires_at - 60:  # Refresh 1 minute before expiry
                return self._access_token
        
        logger.info("Acquiring new access token from Microsoft Graph...")
        
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        token_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://graph.microsoft.com/.default',
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(token_url, data=token_data, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Token request failed with status {response.status_code}")
                try:
                    error_details = response.json()
                    logger.error(f"Token error details: {error_details}")
                except:
                    logger.error(f"Raw token error response: {response.text}")
                raise Exception(f"Failed to acquire access token: {response.status_code}")
            
            token_json = response.json()
            
            if 'access_token' not in token_json:
                logger.error("No access token in response")
                raise Exception("Invalid token response from Microsoft Graph")
            
            self._access_token = token_json['access_token']
            
            # Calculate token expiry time
            import time
            expires_in = token_json.get('expires_in', 3600)  # Default to 1 hour
            self._token_expires_at = time.time() + expires_in
            
            logger.info("Successfully acquired access token")
            return self._access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during token acquisition: {e}")
            raise Exception(f"Network error acquiring access token: {e}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authorization token"""
        access_token = self._get_access_token()
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_all_employees(self, site_filter: str = "Limerick, Limerick Raheen Business Park", 
                         domain_filter: str = "@stryker.com") -> List[Dict[str, Any]]:
        """
        Fetch all employees from Microsoft Graph API with optional filtering
        
        Args:
            site_filter: Office location to filter by
            domain_filter: Email domain to filter by
            
        Returns:
            List of employee dictionaries with keys: first_name, last_name, email, department
        """
        logger.info("Fetching employees from Microsoft Graph API...")
        
        headers = self._get_headers()
        users_url = "https://graph.microsoft.com/v1.0/users"
        params = {
            '$select': 'givenName,surname,userPrincipalName,department,officeLocation',
            '$top': 999  # Get maximum per request
        }
        
        all_users = []
        next_link = users_url
        
        while next_link:
            try:
                if next_link == users_url:
                    response = requests.get(next_link, headers=headers, params=params, timeout=60)
                else:
                    response = requests.get(next_link, headers=headers, timeout=60)
                
                if response.status_code != 200:
                    logger.error(f"Graph API request failed with status {response.status_code}")
                    try:
                        error_details = response.json()
                        logger.error(f"Graph API error details: {error_details}")
                    except:
                        logger.error(f"Raw Graph API error response: {response.text}")
                    raise Exception(f"Graph API request failed: {response.status_code}")
                
                data = response.json()
                
                # Filter users by site and domain if filters are provided
                users_batch = data.get('value', [])
                if site_filter and domain_filter:
                    filtered_users = [
                        user for user in users_batch
                        if (user.get('officeLocation') == site_filter and 
                            user.get('userPrincipalName', '').lower().endswith(domain_filter.lower()))
                    ]
                else:
                    filtered_users = users_batch
                
                all_users.extend(filtered_users)
                next_link = data.get('@odata.nextLink')
                
                logger.info(f"Fetched {len(users_batch)} users, filtered to {len(filtered_users)} matching users")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching users from Graph API: {e}")
                raise Exception(f"Network error fetching employees: {e}")
        
        logger.info(f"Total matching users found: {len(all_users)}")
        
        # Convert to standardized format
        employees_data = []
        for user in all_users:
            # Handle None values from Microsoft Graph API
            first_name = user.get('givenName') or ''
            last_name = user.get('surname') or ''
            email = user.get('userPrincipalName') or ''
            department = user.get('department') or ''
            
            employees_data.append({
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'department': department
            })
        
        # Sort by last name, then first name
        employees_data.sort(key=lambda x: ((x['last_name'] or '').lower(), (x['first_name'] or '').lower()))
        
        return employees_data
    
    def get_user_profile_picture(self, email: str) -> Optional[str]:
        """
        Get user's profile picture from Microsoft Graph API
        
        Args:
            email: User's email address
            
        Returns:
            Base64-encoded profile picture string, or None if not found/error
        """
        logger.info(f"Fetching profile picture for user: {email}")
        
        try:
            headers = self._get_headers()
            
            # Get user ID first (Microsoft Graph requires user ID for photo endpoint)
            user_url = f"https://graph.microsoft.com/v1.0/users/{email}"
            user_response = requests.get(user_url, headers=headers, timeout=30)
            
            if user_response.status_code == 404:
                logger.warning(f"User not found: {email}")
                return None
            elif user_response.status_code != 200:
                logger.error(f"Failed to get user info for {email}: {user_response.status_code}")
                return None
            
            user_data = user_response.json()
            user_id = user_data.get('id')
            
            if not user_id:
                logger.error(f"No user ID found for {email}")
                return None
            
            # Get the profile photo
            photo_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/photo/$value"
            photo_response = requests.get(photo_url, headers=headers, timeout=30)
            
            if photo_response.status_code == 404:
                logger.info(f"No profile picture found for user: {email}")
                return None
            elif photo_response.status_code != 200:
                logger.warning(f"Failed to get profile picture for {email}: {photo_response.status_code}")
                return None
            
            # Convert image to base64
            photo_data = photo_response.content
            if not photo_data:
                logger.warning(f"Empty profile picture data for user: {email}")
                return None
            
            # Detect content type from response headers
            content_type = photo_response.headers.get('content-type', 'image/jpeg')
            
            # Encode as base64 with data URL prefix
            base64_image = base64.b64encode(photo_data).decode('utf-8')
            data_url = f"data:{content_type};base64,{base64_image}"
            
            logger.info(f"Successfully retrieved profile picture for {email} (size: {len(photo_data)} bytes)")
            return data_url
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching profile picture for {email}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching profile picture for {email}: {e}")
            return None
    
    def get_user_info(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get basic user information from Microsoft Graph API
        
        Args:
            email: User's email address
            
        Returns:
            Dictionary with user info, or None if not found/error
        """
        logger.info(f"Fetching user info for: {email}")
        
        try:
            headers = self._get_headers()
            user_url = f"https://graph.microsoft.com/v1.0/users/{email}"
            params = {
                '$select': 'givenName,surname,userPrincipalName,department,officeLocation,displayName'
            }
            
            response = requests.get(user_url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 404:
                logger.warning(f"User not found: {email}")
                return None
            elif response.status_code != 200:
                logger.error(f"Failed to get user info for {email}: {response.status_code}")
                return None
            
            user_data = response.json()
            
            return {
                'first_name': user_data.get('givenName', ''),
                'last_name': user_data.get('surname', ''),
                'email': user_data.get('userPrincipalName', ''),
                'department': user_data.get('department', ''),
                'office_location': user_data.get('officeLocation', ''),
                'display_name': user_data.get('displayName', ''),
                'id': user_data.get('id', '')
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching user info for {email}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching user info for {email}: {e}")
            return None


# Convenience functions for backward compatibility and easy use
def get_all_employees() -> List[Dict[str, Any]]:
    """
    Get all employees using default filtering (Limerick site, @stryker.com domain)
    
    Returns:
        List of employee dictionaries
    """
    try:
        client = MicrosoftGraphClient()
        return client.get_all_employees()
    except Exception as e:
        logger.error(f"Failed to get employees: {e}")
        return []

def get_user_profile_picture(email: str) -> Optional[str]:
    """
    Get user's profile picture as base64 data URL
    
    Args:
        email: User's email address
        
    Returns:
        Base64 data URL string, or None if not found
    """
    try:
        client = MicrosoftGraphClient()
        return client.get_user_profile_picture(email)
    except Exception as e:
        logger.error(f"Failed to get profile picture for {email}: {e}")
        return None

def get_user_info(email: str) -> Optional[Dict[str, Any]]:
    """
    Get user information from Microsoft Graph
    
    Args:
        email: User's email address
        
    Returns:
        User info dictionary, or None if not found
    """
    try:
        client = MicrosoftGraphClient()
        return client.get_user_info(email)
    except Exception as e:
        logger.error(f"Failed to get user info for {email}: {e}")
        return None 
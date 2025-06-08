/**
 * Simple Profile Picture Loading
 * Loads and caches user profile pictures from Microsoft Graph API
 */

document.addEventListener('DOMContentLoaded', function() {
  const profileImg = document.getElementById('user-profile-pic');
  const defaultIcon = document.getElementById('default-profile-icon');
  
  if (!profileImg) {
    return;
  }

  const userEmail = profileImg.getAttribute('data-user-email');
  if (!userEmail) {
    showDefaultIcon();
    return;
  }

  const cacheKey = 'profile_pic_' + userEmail;
  const cacheTimeKey = 'profile_pic_time_' + userEmail;
  const now = Date.now();
  const cacheExpiry = 24 * 60 * 60 * 1000; // 24 hours
  
  // Check for cached profile picture
  const cachedPic = localStorage.getItem(cacheKey);
  const cacheTime = localStorage.getItem(cacheTimeKey);
  
  if (cachedPic && cacheTime && (now - parseInt(cacheTime)) < cacheExpiry) {
    // Use cached profile picture
    showProfilePicture(cachedPic);
  } else {
    // Fetch fresh profile picture from API
    fetch('/api/profile-picture/' + encodeURIComponent(userEmail))
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('No profile picture available');
      })
      .then(data => {
        if (data.profile_picture) {
          showProfilePicture(data.profile_picture);
          
          // Cache the profile picture
          localStorage.setItem(cacheKey, data.profile_picture);
          localStorage.setItem(cacheTimeKey, now.toString());
        } else {
          showDefaultIcon();
        }
      })
      .catch(() => {
        showDefaultIcon();
      });
  }
  
  // Handle image load errors
  profileImg.addEventListener('error', showDefaultIcon);
  
  // Clean up old cache entries (older than 7 days)
  cleanupOldCache();

  function showProfilePicture(imageSrc) {
    profileImg.src = imageSrc;
    profileImg.style.display = 'inline-block';
    if (defaultIcon) {
      defaultIcon.style.display = 'none';
    }
  }

  function showDefaultIcon() {
    profileImg.style.display = 'none';
    if (defaultIcon) {
      defaultIcon.style.display = 'inline-block';
    }
  }

  function cleanupOldCache() {
    const cleanupExpiry = 7 * 24 * 60 * 60 * 1000; // 7 days
    Object.keys(localStorage).forEach(key => {
      if (key.startsWith('profile_pic_time_')) {
        const cacheTime = localStorage.getItem(key);
        if (cacheTime && (Date.now() - parseInt(cacheTime)) > cleanupExpiry) {
          localStorage.removeItem(key);
          localStorage.removeItem(key.replace('_time_', '_'));
        }
      }
    });
  }
}); 
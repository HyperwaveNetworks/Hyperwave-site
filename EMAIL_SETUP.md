# Email Configuration Setup for Hyperwave Networks

## Overview
The contact form is configured to send emails to `Info@hyperwave.co.ke` but requires proper Gmail SMTP configuration to work.

## Current Status
- ✅ Contact form is properly configured
- ✅ Professional email templates are ready
- ⚠️ Email SMTP credentials need to be configured

## Setup Instructions

### Option 1: Environment Variables (Recommended)
1. Set these environment variables in your system:
   ```bash
   EMAIL_HOST_USER=Info@hyperwave.co.ke
   EMAIL_HOST_PASSWORD=your_16_character_app_password
   ```

### Option 2: Direct Configuration
Update `hyperwave/settings.py` lines:
```python
EMAIL_HOST_USER = 'Info@hyperwave.co.ke'
EMAIL_HOST_PASSWORD = 'your_app_password_here'
```

## Gmail App Password Setup
1. Sign in to Google Account for `Info@hyperwave.co.ke`
2. Go to Security settings
3. Enable 2-Factor Authentication (if not already enabled)
4. Go to "App passwords" section
5. Generate a new app password for "Django Application"
6. Use the 16-character password in your configuration

## Testing
1. Update the credentials
2. Restart the Django server
3. Submit a test message through the contact form
4. Check both the recipient email and sender confirmation

## Features
- ✅ Professional email formatting
- ✅ Automatic confirmation emails to senders
- ✅ Error handling and user feedback
- ✅ Field validation
- ✅ Responsive design

## Troubleshooting
- If emails don't send, check the Django console for error messages
- Ensure 2FA is enabled on the Gmail account
- Verify the app password is correctly copied (no spaces)
- Check that "Less secure app access" is disabled (use app passwords instead)

## Contact
For technical support: +254 731 567993 
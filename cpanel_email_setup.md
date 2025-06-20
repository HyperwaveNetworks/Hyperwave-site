# cPanel Email Configuration for Hyperwave Networks

## Overview
Since `info@hyperwave.co.ke` is hosted on cPanel, we need to use cPanel's SMTP settings instead of Gmail.

## Current Configuration
The Django settings have been updated to use:
- **SMTP Server**: `mail.hyperwave.co.ke`
- **Port**: 587 (TLS)
- **Username**: `info@hyperwave.co.ke`
- **Password**: `Hyp3rw@V3N3t`

## cPanel SMTP Settings Options

### Option 1: Standard TLS (Port 587) - Current
```python
EMAIL_HOST = 'mail.hyperwave.co.ke'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
```

### Option 2: SSL (Port 465) - Alternative
```python
EMAIL_HOST = 'mail.hyperwave.co.ke'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
```

### Option 3: Alternative Hostname
```python
EMAIL_HOST = 'hyperwave.co.ke'  # Sometimes works better
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

## Troubleshooting Steps

### 1. Verify Email Account in cPanel
- Log into your cPanel hosting control panel
- Go to **Email Accounts**
- Ensure `info@hyperwave.co.ke` exists and is active
- Check the mailbox quota (shouldn't be full)

### 2. Check Email Password
- In cPanel, you can reset the password for `info@hyperwave.co.ke`
- Update the password in `hyperwave/settings.py`
- The password should be the actual email account password, not an app password

### 3. Test SMTP Connection
Run the test script:
```bash
python test_email.py
```

### 4. Common cPanel Email Issues

**Authentication Failed:**
- Wrong email password
- Email account suspended or doesn't exist
- Mailbox quota exceeded

**Connection Refused:**
- Wrong SMTP server hostname
- Port blocked by firewall
- Hosting provider restrictions

**Timeout Errors:**
- Network connectivity issues
- Server temporarily unavailable

## Alternative SMTP Servers to Try

If `mail.hyperwave.co.ke` doesn't work, try these:
1. `hyperwave.co.ke`
2. `smtp.hyperwave.co.ke`
3. `mail.your-hosting-provider.com` (check with your hosting provider)

## Testing Process

1. **Update settings** with correct cPanel configuration
2. **Run test script**: `python test_email.py`
3. **Check for errors** and adjust settings if needed
4. **Test contact form** on the website
5. **Monitor email delivery** to info@hyperwave.co.ke

## When Configuration is Working

Once emails are sending successfully:
1. Change the email backend back to SMTP in `settings.py`:
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   ```
2. Test the contact form on your website
3. Check that emails are received at info@hyperwave.co.ke

## Contact Information
- **Hosting Provider**: Check with your hosting provider for specific SMTP settings
- **Technical Support**: +254 731 567993
- **Email**: info@hyperwave.co.ke (once working!)

## Next Steps
1. Run `python test_email.py` to test the new cPanel configuration
2. If successful, update the EMAIL_BACKEND to 'smtp' in settings.py
3. Test the contact form on your website 
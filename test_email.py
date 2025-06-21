#!/usr/bin/env python
"""
Email Test Script for Hyperwave Networks
Tests email configuration and sending functionality
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyperwave.settings')
django.setup()

from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from datetime import datetime

def test_basic_email():
    """Test basic email sending functionality"""
    print("🧪 Testing Basic Email Functionality...")
    
    try:
        result = send_mail(
            subject='Hyperwave Networks - Email Test',
            message='This is a test email from Hyperwave Networks security system.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['admin@hyperwave.co.ke'],
            fail_silently=False,
        )
        
        if result:
            print("✅ Basic email test: SUCCESS")
            return True
        else:
            print("❌ Basic email test: FAILED - No result returned")
            return False
            
    except Exception as e:
        print(f"❌ Basic email test: FAILED - {str(e)}")
        return False

def test_html_email():
    """Test HTML email sending"""
    print("\n🧪 Testing HTML Email Functionality...")
    
    try:
        html_content = """
        <html>
        <body>
            <h2>🛡️ Hyperwave Networks Security Test</h2>
            <p>This is an HTML email test from your security system.</p>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 5px;">
                <h3>Security Status</h3>
                <ul>
                    <li>✅ DDoS Protection: Active</li>
                    <li>✅ Rate Limiting: Active</li>
                    <li>✅ Admin Security: Active</li>
                    <li>✅ Email System: Testing...</li>
                </ul>
            </div>
            <p><strong>Timestamp:</strong> {timestamp}</p>
            <hr>
            <p><em>Hyperwave Networks - Leading ICT Solutions in Kenya</em></p>
        </body>
        </html>
        """.format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        email = EmailMessage(
            subject='Hyperwave Networks - HTML Email Test',
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['admin@hyperwave.co.ke'],
        )
        email.content_subtype = 'html'
        
        result = email.send()
        
        if result:
            print("✅ HTML email test: SUCCESS")
            return True
        else:
            print("❌ HTML email test: FAILED - No result returned")
            return False
            
    except Exception as e:
        print(f"❌ HTML email test: FAILED - {str(e)}")
        return False

def test_contact_form_email():
    """Test contact form email functionality"""
    print("\n🧪 Testing Contact Form Email...")
    
    try:
        # Simulate contact form submission
        contact_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Email System Test',
            'message': 'This is a test message from the contact form to verify email functionality.'
        }
        
        # Email to admin
        admin_subject = f"New Contact Form Submission: {contact_data['subject']}"
        admin_message = f"""
New contact form submission from Hyperwave Networks website:

Name: {contact_data['name']}
Email: {contact_data['email']}
Subject: {contact_data['subject']}

Message:
{contact_data['message']}

---
This email was sent automatically from the Hyperwave Networks contact form.
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        admin_result = send_mail(
            subject=admin_subject,
            message=admin_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        
        # Confirmation email to user
        user_subject = "Thank you for contacting Hyperwave Networks"
        user_message = f"""
Dear {contact_data['name']},

Thank you for contacting Hyperwave Networks. We have received your message regarding "{contact_data['subject']}" and will respond within 24 hours.

Your message:
{contact_data['message']}

Best regards,
Hyperwave Networks Team
Leading ICT Solutions in Kenya

---
This is an automated confirmation email.
        """
        
        user_result = send_mail(
            subject=user_subject,
            message=user_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact_data['email']],
            fail_silently=False,
        )
        
        if admin_result and user_result:
            print("✅ Contact form email test: SUCCESS")
            print(f"   📧 Admin notification: Sent")
            print(f"   📧 User confirmation: Sent")
            return True
        else:
            print("❌ Contact form email test: PARTIAL FAILURE")
            print(f"   📧 Admin notification: {'✅' if admin_result else '❌'}")
            print(f"   📧 User confirmation: {'✅' if user_result else '❌'}")
            return False
            
    except Exception as e:
        print(f"❌ Contact form email test: FAILED - {str(e)}")
        return False

def test_security_alert_email():
    """Test security alert email functionality"""
    print("\n🧪 Testing Security Alert Email...")
    
    try:
        alert_subject = "🚨 Hyperwave Networks - Security Alert Test"
        alert_message = """
SECURITY ALERT - TEST

This is a test security alert from the Hyperwave Networks security monitoring system.

Alert Details:
- Type: Email System Test
- Severity: INFO
- Timestamp: {timestamp}
- Source: Security Monitor
- Status: Testing email delivery system

System Status:
✅ DDoS Protection: Active
✅ Rate Limiting: Active  
✅ Admin Security: Active
✅ SSL Enforcement: Active
✅ Email Alerts: Testing...

This is a test alert. No action required.

---
Hyperwave Networks Security System
Automated Alert System
        """.format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        result = send_mail(
            subject=alert_subject,
            message=alert_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['admin@hyperwave.co.ke'],
            fail_silently=False,
        )
        
        if result:
            print("✅ Security alert email test: SUCCESS")
            return True
        else:
            print("❌ Security alert email test: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Security alert email test: FAILED - {str(e)}")
        return False

def check_email_configuration():
    """Check email configuration settings"""
    print("🔧 Checking Email Configuration...")
    print(f"📧 Email Backend: {settings.EMAIL_BACKEND}")
    print(f"📧 Email Host: {settings.EMAIL_HOST}")
    print(f"📧 Email Port: {settings.EMAIL_PORT}")
    print(f"📧 Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"📧 Default From: {settings.DEFAULT_FROM_EMAIL}")
    
    if settings.DEBUG:
        print(f"📧 File Path: {getattr(settings, 'EMAIL_FILE_PATH', 'Not set')}")
        print("⚠️  DEBUG mode: Emails will be saved to file instead of sent")
    else:
        print("✅ Production mode: Emails will be sent via SMTP")

def main():
    """Run all email tests"""
    print("🛡️ Hyperwave Networks Email System Test")
    print("=" * 50)
    
    # Check configuration first
    check_email_configuration()
    print("\n" + "=" * 50)
    
    # Run tests
    tests = [
        test_basic_email,
        test_html_email,
        test_contact_form_email,
        test_security_alert_email,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Email Test Results Summary")
    print(f"✅ Passed: {passed}/{total} tests")
    
    if passed == total:
        print("🎉 All email tests PASSED! Email system is working correctly.")
    elif passed > 0:
        print("⚠️  Some email tests failed. Check configuration and try again.")
    else:
        print("❌ All email tests FAILED. Please check email configuration.")
    
    # Check for email files in development
    if settings.DEBUG:
        email_dir = getattr(settings, 'EMAIL_FILE_PATH', 'logs/emails')
        if os.path.exists(email_dir):
            email_files = os.listdir(email_dir)
            if email_files:
                print(f"\n📁 Email files saved to: {email_dir}")
                print(f"📄 Files created: {len(email_files)}")
                for file in email_files[-3:]:  # Show last 3 files
                    print(f"   - {file}")
            else:
                print(f"\n📁 Email directory exists but no files found: {email_dir}")
        else:
            print(f"\n📁 Email directory not found: {email_dir}")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python
"""
Test Contact Form Security Settings
Tests that contact forms work properly with the adjusted security middleware
"""

import os
import sys
import django

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyperwave.settings')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

try:
    import requests
    from bs4 import BeautifulSoup
    print("✅ Required packages imported")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Installing required packages...")
    os.system("pip install requests beautifulsoup4")

from django.test import TestCase, Client
from django.urls import reverse

def test_contact_form_accessibility():
    """Test that contact form is accessible and not blocked by security"""
    print("\n🔍 Testing contact form accessibility...")
    
    client = Client()
    
    try:
        # Test GET request to contact page
        response = client.get('/contact/')
        print(f"   Contact page GET status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Contact page loads successfully")
            
            # Check if CSRF token is present
            content = response.content.decode()
            if 'csrfmiddlewaretoken' in content:
                print("   ✅ CSRF token found in form")
            else:
                print("   ⚠️  CSRF token not found in form")
                
        else:
            print(f"   ❌ Contact page failed to load: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error accessing contact page: {e}")

def test_contact_form_submission():
    """Test contact form submission with security middleware"""
    print("\n📝 Testing contact form submission...")
    
    client = Client()
    
    try:
        # First get the page to obtain CSRF token
        response = client.get('/contact/')
        
        if response.status_code != 200:
            print(f"   ❌ Could not get contact page: {response.status_code}")
            return
            
        # Extract CSRF token using simple string parsing
        content = response.content.decode()
        csrf_start = content.find('name="csrfmiddlewaretoken" value="')
        if csrf_start == -1:
            print("   ❌ Could not find CSRF token")
            return
            
        csrf_start += len('name="csrfmiddlewaretoken" value="')
        csrf_end = content.find('"', csrf_start)
        csrf_value = content[csrf_start:csrf_end]
        
        print(f"   ✅ CSRF token obtained: {csrf_value[:20]}...")
        
        # Test form submission
        form_data = {
            'csrfmiddlewaretoken': csrf_value,
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+254700000000',
            'subject': 'Security Test',
            'message': 'Testing contact form with new security settings',
            'service': 'general'
        }
        
        response = client.post('/contact/', data=form_data, follow=True)
        print(f"   Contact form POST status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Contact form submitted successfully")
            
            # Check for success or error messages
            content = response.content.decode()
            if 'thank you' in content.lower() or 'success' in content.lower():
                print("   ✅ Success message found")
            elif 'error' in content.lower() or 'failed' in content.lower():
                print("   ⚠️  Error message found in response")
            else:
                print("   ℹ️  Form processed (no clear success/error message)")
                
        elif response.status_code == 403:
            print("   ❌ Contact form blocked by security (403 Forbidden)")
            content = response.content.decode()
            if len(content) > 200:
                content = content[:200] + "..."
            print(f"   Response content: {content}")
        else:
            print(f"   ❌ Contact form submission failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error submitting contact form: {e}")

def test_live_server():
    """Test live server accessibility"""
    print("\n🌐 Testing live server...")
    
    try:
        import requests
        response = requests.get('http://127.0.0.1:8000/contact/', timeout=5)
        print(f"   Live server contact page status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Live server contact page accessible")
        else:
            print(f"   ⚠️  Live server returned: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Could not connect to live server (may not be running)")
    except Exception as e:
        print(f"   ❌ Error testing live server: {e}")

def main():
    print("🔒 Contact Form Security Test")
    print("=" * 50)
    
    test_contact_form_accessibility()
    test_contact_form_submission()
    test_live_server()
    
    print("\n" + "=" * 50)
    print("🔒 Security Test Complete")
    print("\nIf all tests show ✅, your contact form should work properly!")
    print("If you see ❌, there may still be security issues blocking legitimate users.")

if __name__ == '__main__':
    main() 
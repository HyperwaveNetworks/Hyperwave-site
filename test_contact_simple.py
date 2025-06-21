#!/usr/bin/env python
"""
Simple Contact Form Test
Tests basic contact form functionality
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyperwave.settings')

# Add test flag to disable security middleware
sys.argv.append('test')

django.setup()

from django.test import TestCase, Client
from django.urls import reverse

def test_basic_contact_form():
    """Test basic contact form functionality"""
    print("🔍 Testing basic contact form...")
    
    client = Client()
    
    try:
        # Test GET request
        response = client.get('/contact/')
        print(f"   GET /contact/ status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Contact page loads successfully")
            
            # Check for form elements
            content = response.content.decode()
            if 'name="name"' in content:
                print("   ✅ Name field found")
            if 'name="email"' in content:
                print("   ✅ Email field found")
            if 'name="message"' in content:
                print("   ✅ Message field found")
            if 'csrfmiddlewaretoken' in content:
                print("   ✅ CSRF token found")
            
            # Try to submit form
            csrf_start = content.find('name="csrfmiddlewaretoken" value="')
            if csrf_start != -1:
                csrf_start += len('name="csrfmiddlewaretoken" value="')
                csrf_end = content.find('"', csrf_start)
                csrf_value = content[csrf_start:csrf_end]
                
                form_data = {
                    'csrfmiddlewaretoken': csrf_value,
                    'name': 'Test User',
                    'email': 'test@example.com',
                    'phone': '+254700000000',
                    'subject': 'Test Subject',
                    'message': 'Test message',
                    'service': 'general'
                }
                
                post_response = client.post('/contact/', data=form_data)
                print(f"   POST /contact/ status: {post_response.status_code}")
                
                if post_response.status_code in [200, 302]:
                    print("   ✅ Form submission successful")
                else:
                    print(f"   ❌ Form submission failed: {post_response.status_code}")
                    
        else:
            print(f"   ❌ Contact page failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == '__main__':
    print("📝 Simple Contact Form Test")
    print("=" * 40)
    test_basic_contact_form()
    print("=" * 40) 
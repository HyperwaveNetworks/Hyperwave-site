from django import forms
from django.core.validators import EmailValidator, RegexValidator
from django.utils.html import strip_tags
import re

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s\-\.\']+$',
                message='Name can only contain letters, spaces, hyphens, dots, and apostrophes.'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your full name',
            'required': True
        })
    )
    
    email = forms.EmailField(
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com',
            'required': True
        })
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject of your inquiry',
            'required': True
        })
    )
    
    message = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Please describe your requirements or questions...',
            'required': True
        })
    )

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Strip HTML tags and normalize whitespace
            name = strip_tags(name).strip()
            # Remove multiple spaces
            name = re.sub(r'\s+', ' ', name)
            if len(name) < 2:
                raise forms.ValidationError('Name must be at least 2 characters long.')
        return name

    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if subject:
            # Strip HTML tags and normalize
            subject = strip_tags(subject).strip()
            subject = re.sub(r'\s+', ' ', subject)
            if len(subject) < 3:
                raise forms.ValidationError('Subject must be at least 3 characters long.')
        return subject

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if message:
            # Strip HTML tags and normalize
            message = strip_tags(message).strip()
            message = re.sub(r'\s+', ' ', message)
            if len(message) < 10:
                raise forms.ValidationError('Message must be at least 10 characters long.')
            
            # Check for spam patterns
            spam_patterns = [
                r'http[s]?://[^\s]+',  # URLs
                r'www\.[^\s]+',        # www links
                r'@[^\s]+\.[^\s]+',    # email addresses in message
                r'\b(buy|cheap|free|click here|limited time)\b',  # spam keywords
            ]
            
            for pattern in spam_patterns:
                if re.search(pattern, message.lower()):
                    raise forms.ValidationError('Message contains suspicious content.')
                    
        return message


class ServiceRequestForm(forms.Form):
    SERVICES = [
        ('internet-solutions', 'Internet Solutions'),
        ('network-infrastructure', 'Network Infrastructure'),
        ('security-systems', 'Security Systems'),
        ('ict-consultancy', 'ICT Consultancy'),
    ]
    
    URGENCY_CHOICES = [
        ('low', 'Low - Within a week'),
        ('medium', 'Medium - Within 2-3 days'),
        ('high', 'High - Within 24 hours'),
        ('urgent', 'Urgent - Immediate attention needed'),
    ]
    
    name = forms.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s\-\.\']+$',
                message='Name can only contain letters, spaces, hyphens, dots, and apostrophes.'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    
    email = forms.EmailField(
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?[\d\s\-\(\)]{8,20}$',
                message='Please enter a valid phone number.'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+254 XXX XXXXXX'
        })
    )
    
    company = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company name (optional)'
        })
    )
    
    service = forms.ChoiceField(
        choices=SERVICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    
    urgency = forms.ChoiceField(
        choices=URGENCY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    
    requirements = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Please describe your specific requirements...',
            'required': True
        })
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove all non-digit characters except +
            phone = re.sub(r'[^\d\+]', '', phone)
            if not phone.startswith('+'):
                if phone.startswith('0'):
                    phone = '+254' + phone[1:]  # Convert Kenyan format
                elif phone.startswith('7') or phone.startswith('1'):
                    phone = '+254' + phone      # Add country code
            
            if len(phone) < 10 or len(phone) > 15:
                raise forms.ValidationError('Please enter a valid phone number.')
                
        return phone

    def clean_company(self):
        company = self.cleaned_data.get('company')
        if company:
            company = strip_tags(company).strip()
            company = re.sub(r'\s+', ' ', company)
        return company

    def clean_requirements(self):
        requirements = self.cleaned_data.get('requirements')
        if requirements:
            requirements = strip_tags(requirements).strip()
            requirements = re.sub(r'\s+', ' ', requirements)
            if len(requirements) < 20:
                raise forms.ValidationError('Please provide more detailed requirements (minimum 20 characters).')
        return requirements 
from django.conf import settings

def seo_context(request):
    """Add SEO and business context to all templates"""
    return {
        'site_name': getattr(settings, 'SITE_NAME', 'Hyperwave Networks'),
        'site_description': getattr(settings, 'SITE_DESCRIPTION', 'Leading provider of internet solutions, network infrastructure, and security systems in Kenya'),
        'site_keywords': getattr(settings, 'SITE_KEYWORDS', 'internet solutions Kenya, network infrastructure Nairobi, CCTV installation, fiber internet, wireless internet, ICT consultancy'),
        'business_phone': '+254 731 567993',
        'business_email': 'Info@hyperwave.co.ke',
        'business_address': 'Shopping Mall, Kincar Utawala, Nairobi, Kenya',
        'business_hours': 'Monday - Saturday: 9:00 AM - 6:00 PM, Sunday: Closed',
        'facebook_url': 'https://www.facebook.com/hyperwavetech',
        'instagram_url': 'https://www.instagram.com/hyperwavenetworks/',
        'whatsapp_url': 'https://wa.me/254731567993',
        'current_year': 2025,
    } 
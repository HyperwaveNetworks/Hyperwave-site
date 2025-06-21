from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.http import Http404, JsonResponse, HttpResponse
from django.utils.html import escape
from django.core.cache import cache
from django.db.models import Prefetch
import logging
import json

from .forms import ContactForm, ServiceRequestForm, QuoteRequestForm
from .models import Product, InternetPackage, ServiceArea, ProductCategory, BlogPost, ContactSubmission

logger = logging.getLogger('core')

# Cache home page for 1 hour
@cache_page(60 * 60)
@vary_on_headers('User-Agent')
def home(request):
    """Optimized home view with caching"""
    # Use cache for expensive queries
    cache_key = 'home_page_data'
    data = cache.get(cache_key)
    
    if data is None:
        # Fetch data with optimized queries
        packages = InternetPackage.objects.select_related().filter(is_active=True)[:6]
        featured_products = Product.objects.select_related('category').filter(is_featured=True)[:8]
        recent_posts = BlogPost.objects.select_related('author').filter(is_published=True)[:3]
        
        data = {
            'packages': packages,
            'featured_products': featured_products,
            'recent_posts': recent_posts,
        }
        # Cache for 30 minutes
        cache.set(cache_key, data, 60 * 30)
    
    context = {
        'packages': data['packages'],
        'featured_products': data['featured_products'],
        'recent_posts': data['recent_posts'],
    }
    
    return render(request, 'core/home.html', context)

# Cache about page for 6 hours (content rarely changes)
@cache_page(60 * 60 * 6)
def about(request):
    """About page with long-term caching"""
    return render(request, 'core/about.html')

# Cache services page for 2 hours
@cache_page(60 * 60 * 2)
def services(request):
    """Services page with optimized product loading"""
    cache_key = 'services_page_data'
    categories = cache.get(cache_key)
    
    if categories is None:
        # Optimize with prefetch_related to reduce queries
        categories = ProductCategory.objects.prefetch_related(
            Prefetch('product_set', queryset=Product.objects.filter(is_active=True))
        ).filter(is_active=True)
        cache.set(cache_key, categories, 60 * 60)  # Cache for 1 hour
    
    context = {'categories': categories}
    return render(request, 'core/services.html', context)

# Cache packages page for 1 hour
@cache_page(60 * 60)
def packages(request):
    """Internet packages with caching"""
    cache_key = 'packages_data'
    packages = cache.get(cache_key)
    
    if packages is None:
        packages = InternetPackage.objects.select_related('service_area').filter(is_active=True)
        cache.set(cache_key, packages, 60 * 30)  # Cache for 30 minutes
    
    context = {'packages': packages}
    return render(request, 'core/packages.html', context)

# Cache blog list for 30 minutes
@cache_page(60 * 30)
def blog(request):
    """Blog listing with pagination and caching"""
    cache_key = f'blog_posts_page_{request.GET.get("page", 1)}'
    posts = cache.get(cache_key)
    
    if posts is None:
        posts = BlogPost.objects.select_related('author').filter(is_published=True).order_by('-created_at')
        cache.set(cache_key, posts, 60 * 15)  # Cache for 15 minutes
    
    context = {'posts': posts}
    return render(request, 'core/blog.html', context)

def blog_detail(request):
    """Blog detail with individual post caching"""
    post_id = request.GET.get('id')
    if not post_id:
        return render(request, 'core/blog.html')
    
    cache_key = f'blog_post_{post_id}'
    post = cache.get(cache_key)
    
    if post is None:
        post = get_object_or_404(BlogPost, id=post_id, is_published=True)
        cache.set(cache_key, post, 60 * 60 * 2)  # Cache for 2 hours
    
    # Get related posts (cached separately)
    related_cache_key = f'related_posts_{post_id}'
    related_posts = cache.get(related_cache_key)
    
    if related_posts is None:
        related_posts = BlogPost.objects.filter(
            is_published=True
        ).exclude(id=post_id)[:3]
        cache.set(related_cache_key, related_posts, 60 * 60)  # Cache for 1 hour
    
    context = {
        'post': post,
        'related_posts': related_posts
    }
    return render(request, 'core/blog_detail.html', context)

def products(request):
    products = Product.objects.filter(is_active=True).order_by('order', 'title')
    return render(request, 'core/products.html', {'products': products})

@csrf_protect
@require_http_methods(["GET", "POST"])
def contact(request):
    """Optimized contact form handling"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                # Save to database
                contact_submission = ContactSubmission.objects.create(
                    name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data.get('phone', ''),
                    subject=form.cleaned_data['subject'],
                    message=form.cleaned_data['message'],
                    ip_address=request.META.get('REMOTE_ADDR', '')
                )
                
                # Send email asynchronously (in production, use Celery)
                send_mail(
                    subject=f"New Contact Form Submission: {form.cleaned_data['subject']}",
                    message=f"""
                    New contact form submission:
                    
                    Name: {form.cleaned_data['name']}
                    Email: {form.cleaned_data['email']}
                    Phone: {form.cleaned_data.get('phone', 'Not provided')}
                    Subject: {form.cleaned_data['subject']}
                    
                    Message:
                    {form.cleaned_data['message']}
                    
                    IP Address: {request.META.get('REMOTE_ADDR', 'Unknown')}
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                
                messages.success(request, 'Thank you for your message! We will get back to you soon.')
                logger.info(f"Contact form submitted by {form.cleaned_data['email']}")
                
            except BadHeaderError:
                messages.error(request, 'Invalid header found. Please try again.')
                logger.error("BadHeaderError in contact form")
            except Exception as e:
                messages.error(request, 'Sorry, there was an error sending your message. Please try again.')
                logger.error(f"Error in contact form: {str(e)}")
                
            return render(request, 'core/contact.html', {'form': ContactForm()})
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {'form': form})

@csrf_protect
@require_http_methods(["GET", "POST"])
def service_request(request):
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            # Get cleaned data from form
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            company = form.cleaned_data.get('company', '')
            service = form.cleaned_data['service']
            urgency = form.cleaned_data['urgency']
            requirements = form.cleaned_data['requirements']
            
            # Log the service request
            logger.info(f"Service request from {email} - Service: {service}, Urgency: {urgency}")
            
            # Format email content professionally
            email_subject = f'Service Request: {dict(form.SERVICES)[service]} - {dict(form.URGENCY_CHOICES)[urgency]} Priority'
            email_body = f"""New Service Request - Hyperwave Networks

Client Details:
• Name: {name}
• Email: {email}
• Phone: {phone}
• Company: {company if company else 'Not provided'}
• Service: {dict(form.SERVICES)[service]}
• Urgency: {dict(form.URGENCY_CHOICES)[urgency]}

Requirements:
{requirements}

---
This service request was submitted through the Hyperwave Networks website.
Please follow up with the client at: {email} or {phone}

IP Address: {request.META.get('REMOTE_ADDR', 'Unknown')}
User Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')[:100]}"""
            
            try:
                # Send service request to company
                send_mail(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                
                # Send confirmation email to client
                confirmation_subject = f'Service Request Received - {dict(form.SERVICES)[service]}'
                confirmation_body = f"""Dear {name},

Thank you for your service request! We have received your inquiry for {dict(form.SERVICES)[service]} and appreciate your interest in Hyperwave Networks.

Request Details:
• Service: {dict(form.SERVICES)[service]}
• Priority: {dict(form.URGENCY_CHOICES)[urgency]}
• Contact: {phone}
• Company: {company if company else 'Individual request'}

Our technical team will review your requirements and contact you within the timeframe specified by your urgency level to discuss:
• Site assessment and technical requirements
• Customized solution proposal
• Pricing and timeline
• Next steps

For immediate assistance, please call us at +254 731 567993 or visit our office at:
Shopping Mall, Kincar Utawala, Nairobi, Kenya

Best regards,
The Hyperwave Networks Team

---
Hyperwave Networks
Email: Info@hyperwave.co.ke
Phone: +254 731 567993
Web: www.hyperwave.co.ke"""
                
                send_mail(
                    confirmation_subject,
                    confirmation_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=True,
                )
                
                messages.success(request, f'Thank you {escape(name)}! Your service request for {dict(form.SERVICES)[service]} has been submitted successfully. We will contact you according to your specified urgency level.')
                logger.info(f"Service request email sent successfully to {email}")
                
            except Exception as e:
                logger.error(f"Service request email failed: {str(e)} - From: {email}")
                messages.error(request, 'There was an error sending your service request. Please try again or contact us directly at Info@hyperwave.co.ke or +254 731 567993.')
            
            return redirect('service_request')
        else:
            # Form has validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
    else:
        form = ServiceRequestForm()
    
    return render(request, 'core/service_request.html', {'form': form})

def service_detail(request, slug):
    # Dictionary of detailed service information
    service_details = {
        'internet-solutions': {
            'title': 'Wifi Network Installation',
            'slug': 'internet-solutions',
            'description': (
                "Hyperwave Networks delivers seamless, high-speed wireless connectivity for homes, businesses, and enterprises in Nairobi and beyond. "
                "Our expert team handles every step—from site survey and design to installation, optimization, and ongoing support—ensuring you get the best coverage, speed, and security."
            ),
            'features': [
                'Comprehensive site survey and professional network design for optimal coverage and minimal interference',
                'Installation of the latest WiFi 6/6E access points for faster speeds and more device support',
                'Mesh networking for seamless roaming and zero dead zones, even in large or complex spaces',
                'Advanced security: WPA3 encryption, guest networks, parental controls, and firewall integration',
                'Remote monitoring, proactive maintenance, and 24/7 technical support',
                'Integration with smart home, IoT, and business devices',
                'Scalable solutions for homes, offices, hotels, schools, and multi-dwelling units',
                'Flexible upgrade paths as your needs grow',
                'Expert advice on internet packages, bandwidth, and device compatibility'
            ],
            'packages': [
                {
                    'name': 'Starter Home WiFi',
                    'speed': 'Up to 20Mbps',
                    'price': 'KSh 2,000',
                    'details': 'Perfect for small homes and apartments. Includes router, setup, and coverage for up to 5 devices. Ideal for browsing, streaming, and video calls.'
                },
                {
                    'name': 'Family Mesh WiFi',
                    'speed': 'Up to 50Mbps',
                    'price': 'KSh 4,500',
                    'details': 'Mesh system for whole-home coverage, up to 15 devices, and parental controls. Great for families with multiple users and smart devices.'
                },
                {
                    'name': 'Business Pro WiFi',
                    'speed': 'Up to 100Mbps',
                    'price': 'KSh 9,500',
                    'details': 'Enterprise-grade WiFi for offices, shops, or restaurants. Includes multiple access points, guest network, and remote management. Supports video conferencing, cloud apps, and POS systems.'
                },
                {
                    'name': 'Custom Enterprise WiFi',
                    'speed': 'Custom',
                    'price': 'Contact Us',
                    'details': 'Tailored solutions for hotels, schools, or large businesses. Includes site survey, design, and ongoing support. Scalable for hundreds of users and devices.'
                }
            ],
            'image': 'wifi-modern.jpg'
        },
        'security-systems': {
            'title': 'Security Systems',
            'slug': 'security-systems',
            'description': 'Complete security ecosystems to protect your people, assets, and data.',
            'features': [
                'Smart Surveillance with HD CCTV systems and AI analytics',
                'Access Control using biometric and RFID-based systems',
                'Perimeter Protection with electric fences and automated gates',
                'Cybersecurity solutions with enterprise-grade firewalls'
            ],
            'image': 'security.jpg'
        },
        'network-infrastructure': {
            'title': 'Network Infrastructure',
            'slug': 'network-infrastructure',
            'description': 'Complete network infrastructure design, installation, and management services for businesses, institutions, and data centers across Nairobi and Kenya.',
            'features': [
                'Structured cable management systems for organized and efficient network layouts',
                'Professional rack setup and server room organization with proper ventilation and power distribution',
                'ISP POP (Point of Presence) setup for reliable internet connectivity and redundancy',
                'Private network configurations including VLANs, VPNs, and secure internal communications',
                'Optical fiber layout and installation for high-speed backbone connections',
                'Data center infrastructure including server racks, patch panels, and cooling systems',
                'Enterprise-grade switching and routing equipment installation and configuration',
                'Network monitoring and management systems for 24/7 visibility and control',
                'Redundant network design for high availability and business continuity'
            ],
            'image': 'network infrastrcture.jpg'
        },
        'power-solutions': {
            'title': 'Power Solutions & Backup Systems',
            'slug': 'power-solutions',
            'description': 'Comprehensive power backup and energy solutions to ensure uninterrupted operations for your business, home, or institution. From UPS systems to solar installations, we provide reliable power continuity solutions across Kenya.',
            'features': [
                'Uninterruptible Power Supply (UPS) systems for instant backup power and equipment protection',
                'Solar power installations with battery storage for sustainable and cost-effective energy solutions',
                'Diesel and petrol generators for extended backup power during prolonged outages',
                'Hybrid power systems combining multiple technologies for maximum reliability and efficiency',
                'Power distribution units (PDUs) and electrical panel upgrades for safe power management',
                'Automatic transfer switches for seamless power switching without interruption',
                'Battery backup systems with lithium-ion and lead-acid options for different applications',
                'Power monitoring and management systems for real-time energy consumption tracking',
                'Maintenance contracts and 24/7 support for all power systems and equipment'
            ],
            'image': 'power solutions.jpg'
        },
        'managed-it': {
            'title': 'Managed IT Services',
            'slug': 'managed-it',
            'description': 'Comprehensive IT management and technology solutions to streamline your business operations, enhance productivity, and drive digital transformation. From 24/7 system monitoring to custom software development, we provide complete technology support for businesses of all sizes across Kenya.',
            'features': [
                '24/7 system monitoring and proactive IT support for maximum uptime and performance',
                'Cloud services and data management with secure backup and disaster recovery solutions',
                'VPN setup and network security for secure remote access and data protection',
                'Hardware and software procurement with expert guidance and competitive pricing',
                'IT consultancy and strategic technology planning for business growth and efficiency',
                'Custom software development tailored to your specific business requirements',
                'Professional web development and e-commerce solutions for online presence',
                'Graphic design and branding services for marketing materials and corporate identity',
                'Help desk support and user training for smooth technology adoption'
            ],
            'services': [
                {
                    'name': '24/7 IT Monitoring & Support',
                    'description': 'Round-the-clock monitoring of your IT infrastructure with proactive maintenance and rapid response to issues.',
                    'features': [
                        'Real-time server and network monitoring',
                        'Automatic alerts for system anomalies',
                        'Remote troubleshooting and resolution',
                        'Performance optimization and tuning',
                        'Monthly performance reports and recommendations'
                    ]
                },
                {
                    'name': 'VPN & Network Security',
                    'description': 'Secure virtual private networks and comprehensive network security solutions for safe remote access and data protection.',
                    'features': [
                        'Enterprise VPN setup and configuration',
                        'Multi-factor authentication implementation',
                        'Network firewall management and monitoring',
                        'Secure remote access for employees',
                        'Network vulnerability assessments and security audits'
                    ]
                },
                {
                    'name': 'Cloud Services & Data Management',
                    'description': 'Complete cloud migration, management, and data backup solutions to ensure business continuity and scalability.',
                    'features': [
                        'Cloud migration planning and execution',
                        'Automated backup and disaster recovery',
                        'Cloud storage optimization and cost management',
                        'Microsoft 365 and Google Workspace setup',
                        'Data synchronization across multiple devices'
                    ]
                },
                {
                    'name': 'IT Consultancy & Strategic Planning',
                    'description': 'Expert technology consulting to help you make informed decisions and develop effective IT strategies for business growth.',
                    'features': [
                        'Technology assessment and gap analysis',
                        'IT budget planning and cost optimization',
                        'Digital transformation roadmaps',
                        'Vendor selection and procurement guidance',
                        'Compliance and regulatory consulting'
                    ]
                },
                {
                    'name': 'Custom Software Development',
                    'description': 'Bespoke software solutions designed to meet your unique business requirements and automate complex processes.',
                    'features': [
                        'Business process automation systems',
                        'Customer relationship management (CRM) systems',
                        'Inventory and supply chain management software',
                        'Mobile application development (iOS/Android)',
                        'API development and third-party integrations'
                    ]
                },
                {
                    'name': 'Web Development & E-commerce',
                    'description': 'Professional website development and e-commerce solutions to establish and grow your online presence.',
                    'features': [
                        'Responsive website design and development',
                        'E-commerce platforms and payment integration',
                        'Content management systems (CMS)',
                        'Search engine optimization (SEO)',
                        'Website maintenance and security updates'
                    ]
                },
                {
                    'name': 'Graphic Design & Branding',
                    'description': 'Creative design services to build strong brand identity and effective marketing materials for your business.',
                    'features': [
                        'Logo design and brand identity development',
                        'Marketing materials (brochures, flyers, banners)',
                        'Social media graphics and digital marketing assets',
                        'Business cards and corporate stationery',
                        'Packaging design and product graphics'
                    ]
                }
            ],
            'image': 'it services.jpg'
        }
    }
    
    # Get the service details or return a 404 if not found
    service = service_details.get(slug)
    if not service:
        from django.http import Http404
        raise Http404("Service does not exist")
        
    return render(request, 'core/service_detail.html', {'service': service})

def custom_404(request, exception):
    """Custom 404 error handler"""
    logger.warning(f"404 error for path: {request.path} from IP: {request.META.get('REMOTE_ADDR', 'Unknown')}")
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    """Custom 500 error handler"""
    logger.error(f"500 error for path: {request.path} from IP: {request.META.get('REMOTE_ADDR', 'Unknown')}")
    return render(request, 'errors/500.html', status=500)

@require_http_methods(["POST"])
def quote_request(request):
    """Optimized quote request handling"""
    if request.method == 'POST':
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            try:
                # Send quote request email
                send_mail(
                    subject=f"Quote Request: {form.cleaned_data['service_type']}",
                    message=f"""
                    New quote request:
                    
                    Name: {form.cleaned_data['name']}
                    Email: {form.cleaned_data['email']}
                    Phone: {form.cleaned_data['phone']}
                    Service: {form.cleaned_data['service_type']}
                    
                    Requirements:
                    {form.cleaned_data['requirements']}
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                
                return JsonResponse({'success': True, 'message': 'Quote request sent successfully!'})
                
            except Exception as e:
                logger.error(f"Error in quote request: {str(e)}")
                return JsonResponse({'success': False, 'message': 'Error sending quote request. Please try again.'})
        else:
            return JsonResponse({'success': False, 'message': 'Please check your form data.'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

# Health check endpoint for monitoring
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({'status': 'healthy', 'timestamp': cache.get('last_update', 'unknown')})


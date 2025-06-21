from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.http import Http404
from django.utils.html import escape
import logging
from django.core.cache import cache

from .forms import ContactForm, ServiceRequestForm
from .models import Product, InternetPackage, ServiceArea

logger = logging.getLogger('core')

@cache_page(60 * 5)  # Cache for 5 minutes
def home(request):
    # Get packages from database
    internet_packages = [
        {
            'name': p.name,
            'speed': p.speed,
            'price': p.price,
            'features': p.feature_list(),
        }
        for p in InternetPackage.objects.filter(is_active=True).order_by('order', 'speed')
    ]

    # Get service areas from database
    service_areas = [a.name for a in ServiceArea.objects.filter(is_active=True).order_by('order', 'name')]

    return render(request, 'core/home.html', {
        'internet_packages': internet_packages,
        'service_areas': service_areas,
    })

@cache_page(60 * 15)  # Cache for 15 minutes
def about(request):
    return render(request, 'core/about.html')

@cache_page(60 * 5)  # Cache for 5 minutes
def blog(request):
    blog_posts = [
        {
            'id': 1,
            'title': 'WiFi 6: The Next Generation of Wireless Connectivity for Kenyan Businesses',
            'date': 'June 5, 2025',
            'author': 'John Kamau',
            'excerpt': 'Discover how WiFi 6 technology can transform your business connectivity with faster speeds, better coverage, and improved device support.',
            'image': 'TP-Link Archer AX73 WiFi 6.jpg',
            'category': 'Internet Solutions',
            'content': """
            <p>As businesses in Nairobi and across Kenya continue to digitize their operations, the demand for faster, more reliable wireless connectivity has never been greater. WiFi 6 (802.11ax) represents the latest evolution in wireless technology, offering significant improvements over previous standards.</p>
            
            <h3>What Makes WiFi 6 Different?</h3>
            
            <p><strong>1. Increased Speed and Capacity</strong> - WiFi 6 can deliver speeds up to 9.6 Gbps, nearly three times faster than WiFi 5. More importantly for businesses, it can handle more devices simultaneously without performance degradation.</p>
            
            <p><strong>2. Improved Efficiency</strong> - OFDMA (Orthogonal Frequency Division Multiple Access) allows the router to communicate with multiple devices simultaneously, reducing latency and improving overall network efficiency.</p>
            
            <p><strong>3. Better Battery Life</strong> - Target Wake Time (TWT) allows devices to schedule check-ins with the router, significantly extending battery life for IoT devices and mobile equipment.</p>
            
            <p><strong>4. Enhanced Security</strong> - WiFi 6 includes WPA3 security protocol by default, providing stronger encryption and protection against brute-force attacks.</p>
            
            <h3>Business Applications in Kenya</h3>
            
            <p>For Kenyan businesses, WiFi 6 enables:</p>
            <ul>
                <li>High-quality video conferencing for remote teams</li>
                <li>Seamless cloud application access</li>
                <li>Support for increased IoT device deployments</li>
                <li>Better performance in high-density environments like offices and retail spaces</li>
                <li>Future-proofing for emerging technologies</li>
            </ul>
            
            <p>At Hyperwave Networks, we're helping businesses across Nairobi upgrade to WiFi 6 infrastructure. Contact us for a wireless assessment and see how WiFi 6 can transform your business connectivity.</p>
            """
        },
        {
            'id': 2,
            'title': 'Comprehensive Security Systems: Beyond CCTV in Modern Business Protection',
            'date': 'May 28, 2025',
            'author': 'Sarah Njeri',
            'excerpt': 'Explore how integrated security systems combining CCTV, access control, and cybersecurity create comprehensive protection for businesses.',
            'image': 'advanced CCT Surveillance.jpg',
            'category': 'Security Systems',
            'content': """
            <p>Modern business security extends far beyond traditional CCTV cameras. Today's comprehensive security systems integrate physical and digital protection to create multi-layered defense strategies that protect against evolving threats.</p>
            
            <h3>Integrated Security Components</h3>
            
            <p><strong>1. Advanced CCTV Systems</strong> - Modern IP cameras offer 4K resolution, AI-powered analytics, facial recognition, and real-time alerts. These systems can distinguish between vehicles, people, and animals, reducing false alarms while ensuring genuine threats are detected immediately.</p>
            
            <p><strong>2. Access Control Systems</strong> - From RFID cards to biometric scanners, modern access control creates detailed audit trails while ensuring only authorized personnel access sensitive areas. Integration with HR systems allows automatic provisioning and de-provisioning of access rights.</p>
            
            <p><strong>3. Perimeter Security</strong> - Electric fencing, infrared barriers, and motion detection create secure boundaries around your property. These systems provide early warning of intrusion attempts and can be integrated with lighting and alarm systems.</p>
            
            <p><strong>4. Cybersecurity Integration</strong> - Network security, firewalls, and intrusion detection systems protect your digital assets. When integrated with physical security, these systems provide comprehensive protection against both physical and cyber threats.</p>
            
            <h3>Benefits for Kenyan Businesses</h3>
            
            <ul>
                <li>Reduced security personnel costs through automation</li>
                <li>Comprehensive incident documentation for insurance and legal purposes</li>
                <li>Remote monitoring capabilities for multiple locations</li>
                <li>Integration with business systems for enhanced operational efficiency</li>
                <li>Scalable solutions that grow with your business</li>
            </ul>
            
            <p>Hyperwave Networks designs and implements integrated security solutions for businesses, institutions, and residential complexes across Kenya. Our systems combine the latest technology with local expertise to provide effective, reliable protection.</p>
            """
        },
        {
            'id': 3,
            'title': 'Fiber vs. Wireless: Choosing the Right Internet Connection for Your Business',
            'date': 'May 20, 2025',
            'author': 'Michael Omondi',
            'excerpt': 'Compare fiber optic and wireless internet solutions to determine the best connectivity option for your business needs and location.',
            'image': 'Optical Fiber Layout & Installation.jpg',
            'category': 'Internet Solutions',
            'content': """
            <p>Choosing the right internet connectivity for your business is crucial for productivity, growth, and competitive advantage. In Kenya's evolving telecommunications landscape, businesses have more options than ever, but understanding the differences is key to making the right choice.</p>
            
            <h3>Fiber Optic Connectivity</h3>
            
            <p><strong>Advantages:</strong></p>
            <ul>
                <li>Highest speeds available (up to 1Gbps and beyond)</li>
                <li>Symmetrical upload and download speeds</li>
                <li>Most reliable connection with minimal weather interference</li>
                <li>Low latency ideal for real-time applications</li>
                <li>Future-proof technology with room for speed upgrades</li>
            </ul>
            
            <p><strong>Considerations:</strong></p>
            <ul>
                <li>Requires fiber infrastructure to be available in your area</li>
                <li>Installation may take longer if new fiber runs are needed</li>
                <li>Higher upfront costs but better long-term value</li>
            </ul>
            
            <h3>Wireless Connectivity</h3>
            
            <p><strong>Advantages:</strong></p>
            <ul>
                <li>Faster deployment - can be installed within days</li>
                <li>Available in areas where fiber hasn't been deployed</li>
                <li>Lower initial installation costs</li>
                <li>Redundancy option when combined with fiber</li>
                <li>Portable solutions for temporary locations</li>
            </ul>
            
            <p><strong>Considerations:</strong></p>
            <ul>
                <li>Speed limitations compared to fiber</li>
                <li>Potential interference from weather or obstacles</li>
                <li>Shared bandwidth in some deployment models</li>
            </ul>
            
            <h3>Making the Right Choice</h3>
            
            <p>The best connectivity solution depends on your specific needs:</p>
            <ul>
                <li><strong>High-bandwidth applications</strong>: Fiber is ideal for video conferencing, cloud applications, and large file transfers</li>
                <li><strong>Quick deployment needs</strong>: Wireless solutions can be deployed rapidly for immediate connectivity</li>
                <li><strong>Budget considerations</strong>: Wireless offers lower upfront costs, while fiber provides better long-term value</li>
                <li><strong>Redundancy requirements</strong>: Many businesses use both technologies for maximum reliability</li>
            </ul>
            
            <p>At Hyperwave Networks, we assess your location, requirements, and growth plans to recommend the optimal connectivity solution. We provide both fiber and wireless solutions across Nairobi and can design hybrid approaches for maximum reliability.</p>
            """
        },
        {
            'id': 4,
            'title': 'Building Scalable Network Infrastructure: A Guide for Growing Businesses',
            'date': 'May 12, 2025',
            'author': 'David Mwangi',
            'excerpt': 'Learn how to design and implement network infrastructure that supports your current needs while accommodating future growth.',
            'image': 'Structured Cable Management.jpg',
            'category': 'Network Infrastructure',
            'content': """
            <p>As businesses in Kenya grow and embrace digital transformation, their network infrastructure must evolve to support increased demands. Building scalable network infrastructure from the start saves costs and prevents disruptions down the road.</p>
            
            <h3>Core Infrastructure Components</h3>
            
            <p><strong>1. Structured Cabling Systems</strong></p>
            <p>A well-designed structured cabling system is the foundation of any reliable network. Key considerations include:</p>
            <ul>
                <li>Category 6A or fiber optic cables for future-proofing</li>
                <li>Proper cable management for organization and airflow</li>
                <li>Adequate pathway capacity for future expansion</li>
                <li>Professional termination and testing</li>
            </ul>
            
            <p><strong>2. Enterprise Switching Infrastructure</strong></p>
            <p>Managed switches provide the intelligence and flexibility needed for business networks:</p>
            <ul>
                <li>VLAN capability for network segmentation</li>
                <li>Quality of Service (QoS) for traffic prioritization</li>
                <li>Power over Ethernet (PoE) for device power</li>
                <li>Stackable designs for easy expansion</li>
            </ul>
            
            <p><strong>3. Wireless Infrastructure</strong></p>
            <p>Enterprise wireless systems provide mobility without sacrificing security or performance:</p>
            <ul>
                <li>Centrally managed access points</li>
                <li>Seamless roaming between access points</li>
                <li>Guest network isolation</li>
                <li>Advanced security features</li>
            </ul>
            
            <p><strong>4. Security Appliances</strong></p>
            <p>Next-generation firewalls and security appliances protect your network:</p>
            <ul>
                <li>Deep packet inspection</li>
                <li>Intrusion prevention systems</li>
                <li>VPN termination for remote access</li>
                <li>Content filtering and application control</li>
            </ul>
            
            <h3>Planning for Growth</h3>
            
            <p>Successful network infrastructure planning considers:</p>
            <ul>
                <li><strong>Capacity planning</strong>: Design for 3-5 years of growth</li>
                <li><strong>Redundancy</strong>: Eliminate single points of failure</li>
                <li><strong>Monitoring</strong>: Implement tools for proactive management</li>
                <li><strong>Documentation</strong>: Maintain detailed network documentation</li>
                <li><strong>Standardization</strong>: Use consistent hardware and configurations</li>
            </ul>
            
            <p>Hyperwave Networks specializes in designing scalable network infrastructure for businesses across Kenya. Our experienced team can assess your current needs, plan for future growth, and implement solutions that provide reliable, high-performance connectivity.</p>
            """
        },
        {
            'id': 5,
            'title': 'Power Solutions for Business Continuity: Beyond Basic UPS Systems',
            'date': 'May 5, 2025',
            'author': 'Grace Wanjiku',
            'excerpt': 'Discover comprehensive power backup strategies that keep your business operational during outages while reducing long-term energy costs.',
            'image': 'Hybrid Power Solutions.jpg',
            'category': 'Power Solutions',
            'content': """
            <p>Power interruptions remain a significant challenge for businesses in Kenya, with outages causing lost productivity, data corruption, and revenue losses. Modern power solutions go beyond basic backup systems to provide comprehensive business continuity and energy optimization.</p>
            
            <h3>Comprehensive Power Strategy</h3>
            
            <p><strong>1. Uninterruptible Power Supplies (UPS)</strong></p>
            <p>Modern UPS systems provide more than basic backup power:</p>
            <ul>
                <li>Pure sine wave output protects sensitive equipment</li>
                <li>Network monitoring for remote management</li>
                <li>Automatic voltage regulation for power quality</li>
                <li>Modular designs for easy scaling</li>
                <li>Integration with building management systems</li>
            </ul>
            
            <p><strong>2. Generator Systems</strong></p>
            <p>Standby generators provide extended runtime for longer outages:</p>
            <ul>
                <li>Automatic start and transfer switching</li>
                <li>Natural gas, diesel, or petrol fuel options</li>
                <li>Load bank testing and maintenance programs</li>
                <li>Remote monitoring and alerts</li>
                <li>Paralleling for increased capacity</li>
            </ul>
            
            <p><strong>3. Solar Power Integration</strong></p>
            <p>Solar systems reduce energy costs while providing backup power:</p>
            <ul>
                <li>Grid-tied systems with battery backup</li>
                <li>Net metering for energy cost reduction</li>
                <li>Hybrid inverters for seamless operation</li>
                <li>Battery storage for 24/7 availability</li>
                <li>Remote monitoring and optimization</li>
            </ul>
            
            <h3>Business Benefits</h3>
            
            <p>Comprehensive power solutions provide:</p>
            <ul>
                <li><strong>Business Continuity</strong>: Maintain operations during outages</li>
                <li><strong>Cost Reduction</strong>: Lower energy bills through solar integration</li>
                <li><strong>Equipment Protection</strong>: Prevent damage from power quality issues</li>
                <li><strong>Productivity</strong>: Eliminate downtime-related losses</li>
                <li><strong>Competitive Advantage</strong>: Operate when competitors cannot</li>
            </ul>
            
            <h3>Implementation Considerations</h3>
            
            <p>Successful power solution deployment requires:</p>
            <ul>
                <li>Load analysis to determine power requirements</li>
                <li>Runtime calculations for backup duration</li>
                <li>Integration with existing electrical systems</li>
                <li>Compliance with local electrical codes</li>
                <li>Regular maintenance and testing programs</li>
            </ul>
            
            <p>Hyperwave Networks designs and implements comprehensive power solutions for businesses across Kenya. From UPS systems to solar installations, we provide reliable power infrastructure that keeps your business running.</p>
            """
        },
        {
            'id': 6,
            'title': 'Managed IT Services: Focus on Your Business While We Handle the Technology',
            'date': 'April 28, 2025',
            'author': 'Peter Kiprotich',
            'excerpt': 'Learn how managed IT services can reduce costs, improve security, and free up resources to focus on your core business objectives.',
            'image': 'Network Monitoring & Management.png',
            'category': 'Managed IT Services',
            'content': """
            <p>For many businesses in Kenya, managing IT infrastructure internally can be costly, complex, and distracting from core business activities. Managed IT services provide access to enterprise-level technology expertise without the overhead of maintaining an internal IT department.</p>
            
            <h3>Core Managed IT Services</h3>
            
            <p><strong>1. 24/7 Network Monitoring</strong></p>
            <p>Proactive monitoring prevents issues before they impact your business:</p>
            <ul>
                <li>Real-time alerting for network anomalies</li>
                <li>Performance monitoring and optimization</li>
                <li>Automatic backup verification</li>
                <li>Security event monitoring</li>
                <li>Capacity planning and reporting</li>
            </ul>
            
            <p><strong>2. Cloud Services Management</strong></p>
            <p>Expert management of cloud infrastructure and applications:</p>
            <ul>
                <li>Cloud migration planning and execution</li>
                <li>Multi-cloud management and optimization</li>
                <li>Backup and disaster recovery</li>
                <li>Cost optimization and rightsizing</li>
                <li>Security and compliance management</li>
            </ul>
            
            <p><strong>3. Cybersecurity Services</strong></p>
            <p>Comprehensive protection against evolving threats:</p>
            <ul>
                <li>Firewall management and monitoring</li>
                <li>Endpoint protection and response</li>
                <li>Email security and filtering</li>
                <li>Vulnerability assessments</li>
                <li>Security awareness training</li>
            </ul>
            
            <p><strong>4. Help Desk Support</strong></p>
            <p>Professional support for your team's technology needs:</p>
            <ul>
                <li>Multi-channel support (phone, email, chat)</li>
                <li>Remote troubleshooting and resolution</li>
                <li>Software installation and updates</li>
                <li>User training and documentation</li>
                <li>Asset management and tracking</li>
            </ul>
            
            <h3>Business Benefits</h3>
            
            <p>Managed IT services provide significant advantages:</p>
            <ul>
                <li><strong>Cost Predictability</strong>: Fixed monthly costs instead of unexpected IT expenses</li>
                <li><strong>Access to Expertise</strong>: Benefit from specialized knowledge without hiring full-time staff</li>
                <li><strong>Improved Security</strong>: Professional security management and monitoring</li>
                <li><strong>Enhanced Productivity</strong>: Minimize downtime and technology frustrations</li>
                <li><strong>Focus on Core Business</strong>: Spend time on revenue-generating activities</li>
                <li><strong>Scalability</strong>: Easily adjust services as your business grows</li>
            </ul>
            
            <h3>Custom Development Services</h3>
            
            <p>Beyond standard IT management, we offer custom solutions:</p>
            <ul>
                <li>Bespoke software development</li>
                <li>Web application development</li>
                <li>Mobile app development</li>
                <li>System integration and APIs</li>
                <li>Graphic design and branding</li>
            </ul>
            
            <p>Hyperwave Networks provides comprehensive managed IT services tailored to businesses across Kenya. Our local expertise combined with international best practices ensures reliable, secure, and cost-effective IT operations for your business.</p>
            """
        }
    ]
    
    # If a specific blog post is requested
    post_id = request.GET.get('id')
    if post_id:
        try:
            # Find the specific post
            post_id = int(post_id)
            post = next((p for p in blog_posts if p['id'] == post_id), None)
            if post:
                return render(request, 'core/blog_detail.html', {'post': post})
        except (ValueError, TypeError):
            pass
    
    # Otherwise show the blog list
    return render(request, 'core/blog.html', {'posts': blog_posts})

def products(request):
    products = Product.objects.filter(is_active=True).order_by('order', 'title')
    return render(request, 'core/products.html', {'products': products})

def services(request):
    services_list = [
        {
            'title': 'Internet Solutions',
            'icon': 'network.jpg',
            'description': 'High-speed fiber optic and wireless connections for homes and businesses with dedicated support.',
            'slug': 'internet-solutions'
        },
        {
            'title': 'Security Systems',
            'icon': 'security systems.jpg',
            'description': 'Comprehensive security solutions including CCTV, access control, and perimeter protection systems.',
            'slug': 'security-systems'
        },
        {
            'title': 'Network Infrastructure',
            'icon': 'network infrastrcture.jpg',
            'description': 'Complete network infrastructure design, installation, and management services for businesses, institutions, and data centers across Nairobi and Kenya.',
            'slug': 'network-infrastructure'
        },
        {
            'title': 'Power Solutions',
            'icon': 'power solutions.jpg',
            'description': 'Reliable power backup systems including UPS, solar solutions, and generators for business continuity.',
            'slug': 'power-solutions'
        },
        {
            'title': 'Managed IT Services',
            'icon': 'it services.jpg',
            'description': 'Comprehensive IT management including 24/7 monitoring, cloud services, and cybersecurity protection.',
            'slug': 'managed-it'
        }
    ]
    
    return render(request, 'core/services.html', {'services': services_list})

@csrf_protect
@require_http_methods(["GET", "POST"])
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Get cleaned data from form
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Log the contact form submission
            logger.info(f"Contact form submission from {email} - Subject: {subject}")
            
            # Format email content professionally
            email_subject = f'Contact Form Inquiry: {subject}'
            email_body = f"""New Contact Form Submission - Hyperwave Networks

Contact Details:
• Name: {name}
• Email: {email}
• Subject: {subject}

Message:
{message}

---
This message was sent through the Hyperwave Networks contact form.
Please respond directly to the sender at: {email}

IP Address: {request.META.get('REMOTE_ADDR', 'Unknown')}
User Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')[:100]}"""
            
            try:
                # Send email to company
                send_mail(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                
                # Send confirmation email to sender
                confirmation_subject = f'Thank you for contacting Hyperwave Networks - {subject}'
                confirmation_body = f"""Dear {name},

Thank you for contacting Hyperwave Networks! We have received your message regarding "{subject}" and appreciate your interest in our services.

Our team will review your inquiry and respond within 24 hours during business hours (Monday - Saturday, 9:00 AM - 6:00 PM).

For urgent matters, please feel free to call us at +254 731 567993 or visit our office at:
Shopping Mall, Kincar Utawala, Nairobi, Kenya

Your Original Message:
{message}

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
                
                messages.success(request, f'Thank you {escape(name)}! Your message has been sent successfully. We will get back to you within 24 hours.')
                logger.info(f"Contact form email sent successfully to {email}")
                
            except Exception as e:
                logger.error(f"Contact form email failed: {str(e)} - From: {email}")
                messages.error(request, 'There was an error sending your message. Please try again or contact us directly at Info@hyperwave.co.ke or +254 731 567993.')
            
            return redirect('contact')
        else:
            # Form has validation errors - display them in a user-friendly way
            for field, errors in form.errors.items():
                field_name = {
                    'name': 'Name',
                    'email': 'Email',
                    'subject': 'Subject',
                    'message': 'Message'
                }.get(field, field.title())
                
                for error in errors:
                    messages.error(request, f"{field_name}: {error}")
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

def csrf_failure(request, reason=""):
    """Handle CSRF failures with security logging"""
    logger.warning(f"CSRF failure from {request.META.get('REMOTE_ADDR', 'unknown')}: {reason}")
    
    # Track CSRF failures for potential attack detection
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    cache_key = f"csrf_failures:{ip}"
    failures = cache.get(cache_key, 0)
    cache.set(cache_key, failures + 1, 3600)  # Track for 1 hour
    
    # If too many CSRF failures, it might be an attack
    if failures > 10:
        logger.error(f"Multiple CSRF failures from {ip} - possible attack")
    
    return render(request, 'errors/403.html', {
        'error_message': 'Security token verification failed. Please try again.',
        'error_code': 'CSRF_FAILURE'
    }, status=403)


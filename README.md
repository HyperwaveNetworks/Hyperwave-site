# Hyperwave Networks - Professional Django Website

[![Django](https://img.shields.io/badge/Django-4.2.21-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, responsive Django website for **Hyperwave Networks**, a leading ICT solutions provider in Kenya specializing in network infrastructure, internet connectivity, security systems, and digital transformation services.

## 🌐 Live Website
- **Production:** [hyperwave.co.ke](https://hyperwave.co.ke)
- **Development:** http://127.0.0.1:8000

## 🚀 Features

### Core Functionality
- **Responsive Design** - Mobile-first approach with modern UI/UX
- **Professional Business Website** - Complete corporate presence
- **Blog System** - Dynamic content management with CKEditor
- **Contact Forms** - Lead generation with email integration
- **SEO Optimized** - Meta tags, sitemaps, and search engine friendly URLs
- **Security Enhanced** - Custom middleware and security headers
- **Multi-page Architecture** - Home, About, Services, Blog, Contact pages

### Technical Features
- **Django 4.2.21** - Latest stable Django framework
- **SQLite Database** - Development database (production ready)
- **Static File Handling** - WhiteNoise for efficient static file serving
- **Email Integration** - SMTP configuration for contact forms
- **Admin Panel** - Custom Django admin interface
- **Error Handling** - Custom 404/500 error pages
- **Logging System** - Comprehensive logging configuration

### Business Features
- **Service Showcase** - Internet solutions, security systems, power solutions
- **Product Catalog** - Network equipment and technology products
- **Partner Network** - Display of technology partners and vendors
- **Service Areas** - Coverage across Nairobi and surrounding counties
- **Professional Portfolio** - Case studies and success stories

## 🛠 Technology Stack

- **Backend:** Django 4.2.21, Python 3.8+
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap-inspired responsive design
- **Database:** SQLite (development), PostgreSQL ready (production)
- **Static Files:** WhiteNoise
- **Email:** SMTP integration
- **Version Control:** Git
- **Deployment:** cPanel ready, Heroku compatible

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Virtual environment (recommended)

## 🔧 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Code001deyo/Hyperwave-site.git
cd Hyperwave-site
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv env
env\Scripts\activate

# macOS/Linux
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST=your-email-host
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
```

### 5. Database Setup
```bash
python manage.py migrate
python manage.py collectstatic
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to view the website.

## 📁 Project Structure

```
Hyperwave/
├── blog/                   # Blog application
│   ├── migrations/
│   ├── admin.py
│   └── models.py
├── core/                   # Main application
│   ├── management/
│   │   └── commands/
│   │       └── ddos_monitor.py
│   │
│   ├── migrations/
│   ├── middleware.py       # Custom security middleware
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   └── urls.py            # URL patterns
├── hyperwave/             # Project settings
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI application
├── static/               # Static files (CSS, JS, Images)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/            # HTML templates
│   ├── core/
│   ├── errors/
│   └── base.html
├── media/               # User uploaded files
├── logs/                # Application logs
├── requirements.txt     # Python dependencies
└── manage.py           # Django management script
```

## 🌐 Pages & Features

### Public Pages
- **Home** (`/`) - Landing page with services overview
- **About** (`/about/`) - Company information and team
- **Services** (`/services/`) - Service categories and details
- **Blog** (`/blog/`) - Latest articles and insights
- **Contact** (`/contact/`) - Contact form and information

### Service Categories
- **Internet Solutions** (`/services/internet-solutions/`)
- **Security Systems** (`/services/security-systems/`)
- **Power Solutions** (`/services/power-solutions/`)
- **Network Infrastructure** (`/services/network-infrastructure/`)

### Admin Features
- **Django Admin** (`/admin/`) - Content management system
- **Blog Management** - Create and edit blog posts
- **Contact Form Submissions** - View and manage inquiries

## 🔐 Security Features

- **Custom Security Middleware** - DDoS protection and admin security
- **CSRF Protection** - Cross-site request forgery protection
- **Secure Headers** - Security headers configuration
- **Input Validation** - Form validation and sanitization
- **Error Handling** - Custom error pages and logging

## 📧 Email Configuration

The website includes email functionality for:
- Contact form submissions
- Blog notifications
- Admin notifications

Configure in `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.hyperwave.co.ke'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'info@hyperwave.co.ke'
```

## 🚀 Deployment

### cPanel Deployment
1. Upload files to public_html directory
2. Create virtual environment on server
3. Install requirements
4. Configure database settings
5. Set up domain and SSL

### Heroku Deployment
1. Install Heroku CLI
2. Create Procfile
3. Configure environment variables
4. Deploy using Git

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🛡 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode (True/False) | Yes |
| `ALLOWED_HOSTS` | Allowed host names | Yes |
| `EMAIL_HOST` | Email server host | No |
| `EMAIL_HOST_USER` | Email username | No |
| `EMAIL_HOST_PASSWORD` | Email password | No |

## 📊 Performance

- **Page Load Speed** - Optimized static files and images
- **Mobile Performance** - Responsive design with optimized images
- **SEO Score** - Meta tags, structured data, and semantic HTML
- **Security Score** - Security headers and HTTPS ready

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support & Contact

**Hyperwave Networks**
- **Website:** [hyperwave.co.ke](https://hyperwave.co.ke)
- **Email:** info@hyperwave.co.ke
- **Phone:** +254 700 000 000
- **Location:** Nairobi, Kenya

**Developer Contact:**
- **Email:** hyperwavenetworks21@gmail.com
- **GitHub:** [@Code001deyo](https://github.com/Code001deyo)

## 🏢 About Hyperwave Networks

Hyperwave Networks is a leading ICT solutions provider in Kenya, specializing in:

- **Network Infrastructure** - Fiber optic networks, structured cabling
- **Internet Connectivity** - High-speed internet for businesses and homes
- **Security Systems** - CCTV surveillance, access control
- **Power Solutions** - UPS systems, solar power integration
- **Digital Transformation** - Complete IT solutions for modern businesses

**Service Areas:** Nairobi, Kiambu, Machakos, Kajiado, and surrounding counties.

---

**Built with ❤️ by Hyperwave Networks Team**

*Empowering Kenya's Digital Future* 
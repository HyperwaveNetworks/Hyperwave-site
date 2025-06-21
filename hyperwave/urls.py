"""
URL Configuration for Hyperwave Networks Django Project
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500

# Import views for direct URL mapping
from core import views as core_views

# Custom error handlers
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'

urlpatterns = [
    # Admin URLs - configurable path from settings
    path(getattr(settings, 'ADMIN_URL', 'admin/'), admin.site.urls),
    
    # Core application URLs
    path('', core_views.home, name='home'),
    path('about/', core_views.about, name='about'),
    path('blog/', core_views.blog, name='blog'),
    path('products/', core_views.products, name='products'),
    path('services/', core_views.services, name='services'),
    path('services/<slug:slug>/', core_views.service_detail, name='service_detail'),
    path('contact/', core_views.contact, name='contact'),
    path('service-request/', core_views.service_request, name='service_request'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

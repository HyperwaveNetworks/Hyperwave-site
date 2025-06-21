"""
URL configuration for hyperwave project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views

# Custom error handlers
handler400 = 'core.views.custom_400'
handler403 = 'core.views.custom_403'
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'

# Get admin URL from settings (for security)
admin_url = getattr(settings, 'ADMIN_URL', 'admin/')

urlpatterns = [
    # Admin with custom URL for security
    path(admin_url, admin.site.urls),
    
    # Security endpoints (restricted)
    path('security/health/', views.security_check, name='security_health'),
    
    # Main application URLs
    path('', include('core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site headers for branding
admin.site.site_header = "Hyperwave Networks Administration"
admin.site.site_title = "Hyperwave Admin"
admin.site.index_title = "Welcome to Hyperwave Networks Administration"

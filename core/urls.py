from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('products/', views.products, name='products'),
    path('services/', views.services, name='services'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    
    # Contact and forms
    path('contact/', views.contact, name='contact'),
    path('service-request/', views.service_request, name='service_request'),
]
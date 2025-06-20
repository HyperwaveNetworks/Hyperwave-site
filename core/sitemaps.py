from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from datetime import datetime

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return ['home', 'about', 'services', 'products', 'blog', 'contact', 'service_request']

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        # Return current time for dynamic pages
        return timezone.now()

    def priority(self, item):
        # Set different priorities for different pages
        priorities = {
            'home': 1.0,
            'services': 0.9,
            'products': 0.9,
            'about': 0.8,
            'contact': 0.8,
            'blog': 0.7,
            'service_request': 0.7,
        }
        return priorities.get(item, 0.5)

    def changefreq(self, item):
        # Set different change frequencies for different pages
        frequencies = {
            'home': 'daily',
            'services': 'weekly',
            'products': 'weekly',
            'blog': 'daily',
            'about': 'monthly',
            'contact': 'monthly',
            'service_request': 'monthly',
        }
        return frequencies.get(item, 'monthly')


class ServiceDetailSitemap(Sitemap):
    priority = 0.9
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        # List of service slugs
        return [
            'internet-solutions',
            'network-infrastructure',
            'security-systems',
            'ict-consultancy',
        ]

    def location(self, item):
        return reverse('service_detail', args=[item])

    def lastmod(self, item):
        return timezone.now() 
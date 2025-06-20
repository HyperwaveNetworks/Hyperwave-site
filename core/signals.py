from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import InternetPackage

@receiver(post_save, sender=InternetPackage)
def clear_home_cache_on_save(sender, **kwargs):
    # Clear all cache entries to ensure home page is refreshed
    cache.clear()

@receiver(post_delete, sender=InternetPackage)
def clear_home_cache_on_delete(sender, **kwargs):
    # Clear all cache entries to ensure home page is refreshed
    cache.clear() 
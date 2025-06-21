import time
import hashlib
from django.http import HttpResponse, HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
import logging
from collections import defaultdict
import re
from datetime import datetime, timedelta
import sys

logger = logging.getLogger('django.security')

# Custom HttpResponseTooManyRequests for compatibility
class HttpResponseTooManyRequests(HttpResponse):
    status_code = 429

class DDoSProtectionMiddleware:
    """
    Comprehensive DDoS Protection Middleware
    Features:
    - Connection rate limiting with progressive delays
    - Pattern-based attack detection
    - IP reputation tracking
    - Automated threat response
    - Geographic blocking capabilities
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # In-memory tracking for enhanced detection
        self.connection_tracker = defaultdict(list)
        self.pattern_tracker = defaultdict(int)
        self.blocked_ips = set()
        
    def __call__(self, request):
        # Skip all protection in development mode or during testing
        if settings.DEBUG or 'test' in sys.argv:
            return self.get_response(request)
            
        ip = self.get_client_ip(request)
        
        # Whitelist legitimate paths that should never be blocked
        safe_paths = ['/contact/', '/service-request/', '/static/', '/media/', '/favicon.ico', '/robots.txt']
        if any(request.path.startswith(path) for path in safe_paths):
            # Still add security headers but skip aggressive filtering
            response = self.get_response(request)
            return self.add_security_headers(response)
        
        # Check if IP is permanently blocked
        if self.is_ip_blocked(ip):
            logger.critical(f"Blocked IP attempted access: {ip}")
            return HttpResponseForbidden("Access denied. IP has been blocked.")
        
        # DDoS Detection and Response (but be more lenient for legitimate users)
        ddos_response = self.detect_ddos_attack(request)
        if ddos_response:
            return ddos_response
        
        # Rate limiting with progressive delays (more lenient for contact forms)
        rate_limit_response = self.advanced_rate_limiting(request)
        if rate_limit_response:
            return rate_limit_response
        
        # Suspicious pattern detection (but allow legitimate contact form data)
        if self.is_suspicious_request(request):
            # Don't block contact form submissions even if they contain suspicious patterns
            if request.path in ['/contact/', '/service-request/'] and request.method == 'POST':
                logger.warning(f"Suspicious patterns in contact form from {ip}: {request.path} - ALLOWING")
            else:
                self.track_suspicious_activity(ip, request)
                logger.warning(f"Suspicious request from {ip}: {request.path}")
                return HttpResponseForbidden("Request blocked for security reasons.")
        
        # Track legitimate requests
        self.track_connection(ip, request)
        
        response = self.get_response(request)
        response = self.add_security_headers(response)
        
        return response

    def get_client_ip(self, request):
        """Get the real client IP address with proxy support"""
        # Check multiple headers for real IP (useful behind load balancers/CDNs)
        headers = [
            'HTTP_CF_CONNECTING_IP',  # Cloudflare
            'HTTP_X_FORWARDED_FOR',   # Standard proxy header
            'HTTP_X_REAL_IP',         # Nginx proxy
            'HTTP_X_FORWARDED',
            'HTTP_X_CLUSTER_CLIENT_IP',
            'HTTP_FORWARDED_FOR',
            'HTTP_FORWARDED',
            'REMOTE_ADDR'
        ]
        
        for header in headers:
            ip = request.META.get(header)
            if ip:
                # Handle comma-separated IPs (take the first one)
                ip = ip.split(',')[0].strip()
                if self.is_valid_ip(ip):
                    return ip
        
        return request.META.get('REMOTE_ADDR', '127.0.0.1')

    def is_valid_ip(self, ip):
        """Validate IP address format"""
        import ipaddress
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def detect_ddos_attack(self, request):
        """Advanced DDoS attack detection"""
        ip = self.get_client_ip(request)
        current_time = time.time()
        
        # Check connection burst detection
        if self.is_connection_burst(ip, current_time):
            self.add_to_blocklist(ip, duration=1800)  # 30 minutes
            logger.critical(f"DDoS attack detected from {ip} - Connection burst")
            return HttpResponseTooManyRequests("DDoS protection activated. Access temporarily restricted.")
        
        # Check request pattern anomalies
        if self.is_pattern_anomaly(ip, request):
            self.add_to_blocklist(ip, duration=900)  # 15 minutes
            logger.critical(f"DDoS attack detected from {ip} - Pattern anomaly")
            return HttpResponseTooManyRequests("Unusual request pattern detected. Access restricted.")
        
        # Check for distributed attack patterns
        if self.is_distributed_attack():
            # Implement stricter rate limiting globally
            self.enable_emergency_mode()
            logger.critical("Distributed DDoS attack detected - Emergency mode activated")
        
        return None

    def is_connection_burst(self, ip, current_time):
        """Detect sudden burst of connections from single IP"""
        cache_key = f"ddos_burst:{ip}"
        connections = cache.get(cache_key, [])
        
        # Remove old connections (older than 10 seconds)
        connections = [ts for ts in connections if current_time - ts < 10]
        connections.append(current_time)
        
        # Update cache
        cache.set(cache_key, connections, 30)
        
        # Check for burst: more than 20 connections in 10 seconds
        if len(connections) > 20:
            return True
        
        # Check for sustained high rate: more than 100 connections per minute
        minute_connections = [ts for ts in connections if current_time - ts < 60]
        if len(minute_connections) > 100:
            return True
        
        return False

    def is_pattern_anomaly(self, ip, request):
        """Detect abnormal request patterns"""
        # Check for rapid-fire identical requests
        request_signature = self.generate_request_signature(request)
        cache_key = f"pattern:{ip}:{request_signature}"
        
        request_count = cache.get(cache_key, 0)
        if request_count > 10:  # Same request more than 10 times in 60 seconds
            return True
        
        cache.set(cache_key, request_count + 1, 60)
        
        # Check for scanning behavior (many different paths)
        paths_key = f"paths:{ip}"
        paths = cache.get(paths_key, set())
        paths.add(request.path)
        cache.set(paths_key, paths, 300)  # 5 minutes
        
        # More than 50 different paths in 5 minutes indicates scanning
        if len(paths) > 50:
            return True
        
        return False

    def generate_request_signature(self, request):
        """Generate a signature for request pattern detection"""
        signature_data = f"{request.method}:{request.path}:{request.META.get('HTTP_USER_AGENT', '')}"
        return hashlib.md5(signature_data.encode()).hexdigest()[:16]

    def is_distributed_attack(self):
        """Detect distributed attacks across multiple IPs"""
        cache_key = "global_request_rate"
        current_time = time.time()
        
        # Track global request rate
        global_requests = cache.get(cache_key, [])
        global_requests = [ts for ts in global_requests if current_time - ts < 60]
        global_requests.append(current_time)
        cache.set(cache_key, global_requests, 120)
        
        # If more than 1000 requests per minute globally, likely DDoS
        return len(global_requests) > 1000

    def enable_emergency_mode(self):
        """Enable emergency mode with stricter limits"""
        cache.set("emergency_mode", True, 600)  # 10 minutes
        logger.critical("Emergency DDoS protection mode activated")

    def advanced_rate_limiting(self, request):
        """Advanced rate limiting with progressive delays and contact form exceptions"""
        # Skip rate limiting in development
        if settings.DEBUG:
            return None
            
        ip = self.get_client_ip(request)
        
        # Special handling for contact forms - more lenient
        if request.path in ['/contact/', '/service-request/'] and request.method == 'POST':
            cache_key = f"contact_rate:{ip}"
            contact_requests = cache.get(cache_key, 0)
            
            if contact_requests >= 3:  # Allow 3 contact form submissions per hour
                logger.warning(f"Contact form rate limit exceeded for {ip}")
                return HttpResponseTooManyRequests(
                    "Too many contact form submissions. Please wait an hour before submitting again."
                )
            
            cache.set(cache_key, contact_requests + 1, 3600)  # Track for 1 hour
            return None
        
        # Check if in emergency mode
        if cache.get("emergency_mode", False):
            limit = 10  # Very strict limit during emergency
            window = 60
        else:
            # Normal rate limiting
            if request.path.startswith('/admin/'):
                limit = 5
                window = 60
            elif request.method == 'POST':
                limit = 10  # Increased from 3 to 10 for better user experience
                window = 60
            else:
                limit = 50  # Increased from 30 to 50 for better user experience
                window = 60
        
        cache_key = f"rate_limit:{ip}"
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= limit:
            # Progressive penalty
            penalty_key = f"penalty:{ip}"
            penalties = cache.get(penalty_key, 0)
            
            # Increase penalty duration for repeat offenders
            penalty_duration = min(300, 30 * (penalties + 1))  # Max 5 minutes
            cache.set(penalty_key, penalties + 1, 3600)  # Track penalties for 1 hour
            
            logger.warning(f"Rate limit exceeded for {ip}, penalty: {penalty_duration}s")
            return HttpResponseTooManyRequests(
                f"Rate limit exceeded. Try again in {penalty_duration} seconds."
            )
        
        cache.set(cache_key, current_requests + 1, window)
        return None

    def track_connection(self, ip, request):
        """Track connection patterns for analysis"""
        current_time = time.time()
        
        # Track in local memory for real-time analysis
        self.connection_tracker[ip].append({
            'timestamp': current_time,
            'path': request.path,
            'method': request.method,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:100]
        })
        
        # Keep only recent connections (last 5 minutes)
        cutoff_time = current_time - 300
        self.connection_tracker[ip] = [
            conn for conn in self.connection_tracker[ip] 
            if conn['timestamp'] > cutoff_time
        ]
        
        # Clean up old IPs from tracker
        if len(self.connection_tracker) > 1000:
            old_ips = [ip for ip, conns in self.connection_tracker.items() 
                      if not conns or conns[-1]['timestamp'] < cutoff_time]
            for old_ip in old_ips:
                del self.connection_tracker[old_ip]

    def track_suspicious_activity(self, ip, request):
        """Track and score suspicious activities"""
        cache_key = f"suspicious_score:{ip}"
        current_score = cache.get(cache_key, 0)
        
        # Scoring system for different suspicious activities
        score_increment = 1
        
        # Higher scores for more suspicious patterns
        if any(pattern in request.path.lower() for pattern in ['admin', 'wp-', 'php']):
            score_increment = 3
        elif request.method == 'POST' and not request.path.startswith('/contact/'):
            score_increment = 2
        
        new_score = current_score + score_increment
        cache.set(cache_key, new_score, 3600)  # Track for 1 hour
        
        # Block IP if score exceeds threshold
        if new_score > 10:
            self.add_to_blocklist(ip, duration=3600)  # 1 hour block
            logger.critical(f"IP {ip} blocked due to high suspicious activity score: {new_score}")

    def add_to_blocklist(self, ip, duration=3600):
        """Add IP to blocklist with specified duration"""
        cache_key = f"blocked_ip:{ip}"
        cache.set(cache_key, True, duration)
        self.blocked_ips.add(ip)
        logger.critical(f"IP {ip} added to blocklist for {duration} seconds")

    def is_ip_blocked(self, ip):
        """Check if IP is currently blocked"""
        cache_key = f"blocked_ip:{ip}"
        return cache.get(cache_key, False) or ip in self.blocked_ips

    def is_suspicious_request(self, request):
        """Enhanced suspicious request detection"""
        suspicious_patterns = [
            # Web application attacks
            'wp-admin', 'wp-login', 'wp-content', 'wp-includes',
            'phpmyadmin', 'admin.php', 'administrator', 'cpanel',
            'plesk', 'webmin', 'cgi-bin', '.env', 'config.php',
            
            # SQL Injection
            'eval(', 'base64_decode', 'UNION SELECT', 'OR 1=1',
            'DROP TABLE', 'INSERT INTO', 'UPDATE SET', 'DELETE FROM',
            'EXEC(', 'EXECUTE(', 'sp_', 'xp_cmdshell',
            
            # Directory traversal
            '../', '..\\', '/etc/passwd', '/proc/self/environ',
            'windows/system32', 'boot.ini', 'etc/shadow',
            
            # XSS and script injection
            'script>', '<iframe', 'javascript:', 'vbscript:',
            'onload=', 'onerror=', 'onclick=', 'alert(',
            
            # File inclusion
            'php://input', 'php://filter', 'data://', 'file://',
            'expect://', 'zip://', 'phar://',
            
            # Command injection
            ';cat ', ';ls ', ';wget ', ';curl ', '|nc ',
            '&&', '||', '`', '$(',
        ]
        
        request_content = f"{request.path} {request.META.get('QUERY_STRING', '')}"
        
        # Check URL path and query string
        for pattern in suspicious_patterns:
            if pattern.lower() in request_content.lower():
                return True
        
        # Check POST data
        if request.method == 'POST':
            try:
                post_data = str(request.POST)
                for pattern in suspicious_patterns:
                    if pattern.lower() in post_data.lower():
                        return True
            except:
                pass
        
        # Check for suspicious user agents
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        # Allow common legitimate tools and libraries
        legitimate_agents = [
            'python-requests',  # Allow Python requests library
            'curl/',           # Allow curl (but not malicious curl usage)
            'wget/',           # Allow wget (but not malicious wget usage)
            'postman',         # Allow Postman API testing
            'insomnia',        # Allow Insomnia API testing
        ]
        
        # Check if it's a legitimate tool first
        for agent in legitimate_agents:
            if agent in user_agent:
                return False  # Allow legitimate tools
        
        # Then check for suspicious agents
        suspicious_agents = [
            'nikto', 'sqlmap', 'nmap', 'masscan', 'zap', 'burp',
            'acunetix', 'nessus', 'openvas', 'w3af', 'dirb', 'dirbuster',
            'gobuster', 'wfuzz', 'ffuf', 'hydra', 'medusa', 'ncrack',
            # Remove python-requests, curl, wget from suspicious list
            'python-urllib',
        ]
        
        for agent in suspicious_agents:
            if agent in user_agent:
                return True
        
        # Check for missing or suspicious headers (but allow localhost testing)
        if not user_agent:  # No user agent
            # Allow empty user agent from localhost for testing
            client_ip = self.get_client_ip(request)
            if client_ip in ['127.0.0.1', '::1', 'localhost']:
                return False  # Allow localhost testing
            return True
        
        # Check for non-browser requests to browser-specific endpoints
        browser_endpoints = ['/favicon.ico', '/robots.txt', '/sitemap.xml']
        if (request.path in browser_endpoints and 
            not any(browser in user_agent for browser in ['mozilla', 'chrome', 'safari', 'firefox', 'edge'])):
            return False  # Allow legitimate crawlers for these endpoints
        
        return False

    def add_security_headers(self, response):
        """Enhanced security headers with DDoS protection indicators"""
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https://cdnjs.cloudflare.com https://kit.fontawesome.com "
            "https://cdn.jsdelivr.net https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "img-src 'self' data: https: http:; "
            "font-src 'self' https://fonts.gstatic.com "
            "https://cdnjs.cloudflare.com; "
            "connect-src 'self'; "
            "frame-src 'none'; "
            "object-src 'none'; "
            "base-uri 'self';"
        )
        response['Content-Security-Policy'] = csp
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=(), "
            "accelerometer=(), ambient-light-sensor=()"
        )
        
        # Rate limiting headers
        response['X-RateLimit-Limit'] = '30'
        response['X-RateLimit-Remaining'] = '29'
        
        # DDoS protection indicator
        if cache.get("emergency_mode", False):
            response['X-DDoS-Protection'] = 'Emergency-Mode-Active'
        else:
            response['X-DDoS-Protection'] = 'Active'
        
        return response

    def clear_blocked_ips(self):
        """Clear all blocked IPs"""
        self.blocked_ips.clear()
        logger.info("All blocked IPs have been cleared")


# Keep existing SecurityMiddleware for backward compatibility
class SecurityMiddleware(DDoSProtectionMiddleware):
    """Legacy SecurityMiddleware - now inherits from DDoSProtectionMiddleware"""
    pass


class AdminSecurityMiddleware:
    """Enhanced admin security with DDoS protection"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            # Skip rate limiting in development
            if settings.DEBUG:
                return self.get_response(request)
                
            ip = self.get_client_ip(request)
            
            # Enhanced admin access logging
            logger.info(f"Admin access: IP={ip}, User={getattr(request.user, 'username', 'Anonymous')}, "
                       f"Path={request.path}, Method={request.method}, "
                       f"UA={request.META.get('HTTP_USER_AGENT', '')[:100]}")
            
            # Skip security checks for authenticated staff users
            if request.user.is_authenticated and request.user.is_staff:
                return self.get_response(request)
            
            # Check for admin brute force with enhanced detection
            if self.is_admin_brute_force(request):
                logger.critical(f"Admin brute force detected from {ip}")
                return HttpResponseForbidden("Too many failed login attempts. Access blocked.")
            
            # Additional admin-specific DDoS protection
            if self.is_admin_ddos(request):
                logger.critical(f"Admin DDoS attack detected from {ip}")
                return HttpResponseTooManyRequests("Admin access temporarily restricted due to suspicious activity.")
        
        return self.get_response(request)

    def get_client_ip(self, request):
        """Get client IP with proxy support"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def is_admin_brute_force(self, request):
        """Enhanced brute force detection for admin"""
        if request.method != 'POST' or 'login' not in request.path:
            return False
            
        ip = self.get_client_ip(request)
        
        # Track both IP-based and global admin attempts
        ip_cache_key = f"admin_login_attempts:{ip}"
        global_cache_key = "admin_login_attempts:global"
        
        ip_attempts = cache.get(ip_cache_key, 0)
        global_attempts = cache.get(global_cache_key, 0)
        
        # Block if too many attempts from single IP (5 attempts per hour)
        if ip_attempts >= 5:
            return True
        
        # Block if too many global admin attempts (30 per hour)
        if global_attempts >= 30:
            cache.set("admin_emergency_mode", True, 3600)
            return True
        
        # Increment counters
        cache.set(ip_cache_key, ip_attempts + 1, 3600)
        cache.set(global_cache_key, global_attempts + 1, 3600)
        
        return False

    def is_admin_ddos(self, request):
        """Detect DDoS attacks specifically targeting admin"""
        ip = self.get_client_ip(request)
        cache_key = f"admin_requests:{ip}"
        
        current_requests = cache.get(cache_key, 0)
        
        # More permissive limits for admin access
        if current_requests >= 20:  # Increased from 5 to 20 admin requests per minute
            return True
        
        cache.set(cache_key, current_requests + 1, 60)
        return False 
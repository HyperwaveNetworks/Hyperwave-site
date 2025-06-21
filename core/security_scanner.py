"""
Advanced Security Scanner for Hyperwave Networks
Provides malware detection, trojan protection, and comprehensive threat analysis
"""

import re
import hashlib
import time
import logging
from django.core.cache import cache
from django.conf import settings
from collections import defaultdict
import ipaddress
from datetime import datetime, timedelta

logger = logging.getLogger('security.attacks')

class SecurityScanner:
    """Advanced security scanner for malware and trojan detection"""
    
    def __init__(self):
        self.malware_signatures = self._load_malware_signatures()
        self.trojan_patterns = self._load_trojan_patterns()
        self.suspicious_ips = set()
        self.attack_patterns = defaultdict(int)
        
    def _load_malware_signatures(self):
        """Load known malware signatures and patterns"""
        return {
            # Web shells and backdoors
            'webshells': [
                r'eval\s*\(\s*base64_decode\s*\(',
                r'system\s*\(\s*\$_\w+\[',
                r'exec\s*\(\s*\$_\w+\[',
                r'shell_exec\s*\(\s*\$_\w+\[',
                r'passthru\s*\(\s*\$_\w+\[',
                r'file_get_contents\s*\(\s*["\']php://input',
                r'move_uploaded_file\s*\(\s*\$_FILES',
                r'<?php.*?system\s*\(',
                r'c99shell',
                r'r57shell',
                r'wso\s*shell',
                r'FilesMan',
                r'Uname:.*?php_uname',
            ],
            
            # SQL injection patterns
            'sql_injection': [
                r'union\s+select.*?from',
                r'or\s+1\s*=\s*1',
                r'and\s+1\s*=\s*1',
                r'drop\s+table',
                r'delete\s+from',
                r'insert\s+into',
                r'update\s+.*?set',
                r'exec\s*\(\s*["\']',
                r'sp_executesql',
                r'xp_cmdshell',
                r'information_schema',
                r'load_file\s*\(',
                r'into\s+outfile',
                r'benchmark\s*\(',
                r'sleep\s*\(',
                r'waitfor\s+delay',
            ],
            
            # XSS and script injection
            'xss_patterns': [
                r'<script[^>]*>.*?</script>',
                r'javascript\s*:',
                r'vbscript\s*:',
                r'onload\s*=',
                r'onerror\s*=',
                r'onclick\s*=',
                r'onmouseover\s*=',
                r'onfocus\s*=',
                r'alert\s*\(',
                r'confirm\s*\(',
                r'prompt\s*\(',
                r'document\.cookie',
                r'document\.location',
                r'window\.location',
                r'eval\s*\(',
                r'expression\s*\(',
                r'<iframe[^>]*>',
                r'<object[^>]*>',
                r'<embed[^>]*>',
            ],
            
            # Directory traversal
            'directory_traversal': [
                r'\.\./',
                r'\.\.\\',
                r'/etc/passwd',
                r'/proc/self/environ',
                r'windows/system32',
                r'boot\.ini',
                r'etc/shadow',
                r'%2e%2e%2f',
                r'%2e%2e%5c',
                r'..%252f',
                r'..%255c',
            ],
            
            # Command injection
            'command_injection': [
                r';\s*cat\s+',
                r';\s*ls\s+',
                r';\s*wget\s+',
                r';\s*curl\s+',
                r'\|\s*nc\s+',
                r'&&\s*',
                r'\|\|\s*',
                r'`[^`]+`',
                r'\$\([^)]+\)',
                r'>\s*/dev/null',
                r'2>&1',
                r'/bin/sh',
                r'/bin/bash',
                r'cmd\.exe',
                r'powershell',
            ],
        }
    
    def _load_trojan_patterns(self):
        """Load trojan and backdoor detection patterns"""
        return {
            # Remote access trojans
            'rat_patterns': [
                r'TeamViewer.*?password',
                r'VNC.*?password',
                r'RDP.*?connection',
                r'reverse\s+shell',
                r'bind\s+shell',
                r'netcat.*?-l.*?-p',
                r'socat.*?tcp-listen',
                r'ssh.*?-R\s+\d+',
                r'ngrok.*?tcp',
                r'localtunnel',
            ],
            
            # Data exfiltration
            'exfiltration': [
                r'curl.*?-d.*?@',
                r'wget.*?--post-data',
                r'base64.*?\|\s*curl',
                r'tar.*?\|\s*curl',
                r'zip.*?\|\s*curl',
                r'mysqldump.*?\|\s*curl',
                r'pg_dump.*?\|\s*curl',
                r'scp.*?-r',
                r'rsync.*?-av',
            ],
            
            # Cryptocurrency miners
            'crypto_miners': [
                r'xmrig',
                r'cpuminer',
                r'minerd',
                r'cgminer',
                r'bfgminer',
                r'stratum\+tcp://',
                r'mining\.pool',
                r'cryptonight',
                r'scrypt',
                r'ethash',
                r'equihash',
            ],
            
            # Keyloggers and info stealers
            'info_stealers': [
                r'keylogger',
                r'GetAsyncKeyState',
                r'SetWindowsHookEx',
                r'GetForegroundWindow',
                r'GetWindowText',
                r'clipboard',
                r'screenshot',
                r'browser.*?password',
                r'cookie.*?steal',
                r'credential.*?dump',
            ],
        }
    
    def scan_request_content(self, request):
        """Comprehensive request content scanning"""
        threats_found = []
        
        # Get request content
        content_sources = [
            request.path,
            request.META.get('QUERY_STRING', ''),
            request.META.get('HTTP_USER_AGENT', ''),
            request.META.get('HTTP_REFERER', ''),
        ]
        
        # Add POST data if available
        if request.method == 'POST':
            try:
                content_sources.append(str(request.POST))
                if hasattr(request, 'body'):
                    content_sources.append(request.body.decode('utf-8', errors='ignore'))
            except:
                pass
        
        # Scan each content source
        for content in content_sources:
            if content:
                threats = self._scan_content_for_threats(content)
                threats_found.extend(threats)
        
        return threats_found
    
    def _scan_content_for_threats(self, content):
        """Scan content for malware and trojan patterns"""
        threats = []
        content_lower = content.lower()
        
        # Scan malware signatures
        for category, patterns in self.malware_signatures.items():
            for pattern in patterns:
                if re.search(pattern, content_lower, re.IGNORECASE | re.DOTALL):
                    threats.append({
                        'type': 'malware',
                        'category': category,
                        'pattern': pattern,
                        'severity': 'HIGH',
                        'description': f'Malware pattern detected: {category}'
                    })
        
        # Scan trojan patterns
        for category, patterns in self.trojan_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower, re.IGNORECASE | re.DOTALL):
                    threats.append({
                        'type': 'trojan',
                        'category': category,
                        'pattern': pattern,
                        'severity': 'CRITICAL',
                        'description': f'Trojan pattern detected: {category}'
                    })
        
        return threats
    
    def analyze_ip_reputation(self, ip):
        """Analyze IP reputation and geographic location"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Check if it's a private IP
            if ip_obj.is_private:
                return {'reputation': 'trusted', 'reason': 'private_ip'}
            
            # Check whitelist
            security_config = getattr(settings, 'SECURITY_MIDDLEWARE_CONFIG', {})
            whitelist = security_config.get('WHITELIST_IPS', [])
            if ip in whitelist:
                return {'reputation': 'trusted', 'reason': 'whitelisted'}
            
            # Check cache for known bad IPs
            cache_key = f"ip_reputation:{ip}"
            cached_rep = cache.get(cache_key)
            if cached_rep:
                return cached_rep
            
            # Analyze request patterns from this IP
            reputation = self._analyze_ip_behavior(ip)
            
            # Cache the result
            cache.set(cache_key, reputation, 3600)  # Cache for 1 hour
            
            return reputation
            
        except ValueError:
            return {'reputation': 'suspicious', 'reason': 'invalid_ip'}
    
    def _analyze_ip_behavior(self, ip):
        """Analyze IP behavior patterns"""
        # Get request history for this IP
        history_key = f"ip_history:{ip}"
        history = cache.get(history_key, [])
        
        if len(history) < 5:
            return {'reputation': 'unknown', 'reason': 'insufficient_data'}
        
        # Analyze patterns
        suspicious_indicators = 0
        
        # Check for rapid requests
        if len(history) > 50:
            suspicious_indicators += 1
        
        # Check for diverse path access (scanning behavior)
        unique_paths = len(set(h.get('path', '') for h in history))
        if unique_paths > 20:
            suspicious_indicators += 2
        
        # Check for error rates
        error_count = sum(1 for h in history if h.get('status', 200) >= 400)
        if error_count > len(history) * 0.3:  # More than 30% errors
            suspicious_indicators += 2
        
        # Determine reputation
        if suspicious_indicators >= 3:
            return {'reputation': 'malicious', 'reason': 'suspicious_behavior'}
        elif suspicious_indicators >= 1:
            return {'reputation': 'suspicious', 'reason': 'some_indicators'}
        else:
            return {'reputation': 'clean', 'reason': 'normal_behavior'}
    
    def detect_advanced_threats(self, request):
        """Detect advanced persistent threats and sophisticated attacks"""
        threats = []
        
        # Analyze request timing patterns
        timing_threat = self._analyze_timing_patterns(request)
        if timing_threat:
            threats.append(timing_threat)
        
        # Check for steganography attempts
        stego_threat = self._detect_steganography(request)
        if stego_threat:
            threats.append(stego_threat)
        
        # Analyze user agent for bot patterns
        ua_threat = self._analyze_user_agent(request)
        if ua_threat:
            threats.append(ua_threat)
        
        # Check for encoding obfuscation
        encoding_threat = self._detect_encoding_obfuscation(request)
        if encoding_threat:
            threats.append(encoding_threat)
        
        return threats
    
    def _analyze_timing_patterns(self, request):
        """Analyze request timing for automated attack patterns"""
        ip = self._get_client_ip(request)
        current_time = time.time()
        
        timing_key = f"timing:{ip}"
        timing_data = cache.get(timing_key, [])
        timing_data.append(current_time)
        
        # Keep only last 100 requests
        timing_data = timing_data[-100:]
        cache.set(timing_key, timing_data, 300)
        
        if len(timing_data) < 10:
            return None
        
        # Calculate intervals
        intervals = [timing_data[i] - timing_data[i-1] for i in range(1, len(timing_data))]
        
        # Check for too regular intervals (bot behavior)
        if len(set(round(interval, 1) for interval in intervals[-10:])) <= 2:
            return {
                'type': 'automated_attack',
                'severity': 'HIGH',
                'description': 'Regular timing pattern suggests automated attack'
            }
        
        return None
    
    def _detect_steganography(self, request):
        """Detect potential steganography in requests"""
        # Check for unusual base64 patterns
        content = str(request.GET) + str(getattr(request, 'POST', ''))
        
        base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
        matches = re.findall(base64_pattern, content)
        
        for match in matches:
            if len(match) > 100:  # Suspiciously long base64
                return {
                    'type': 'steganography',
                    'severity': 'MEDIUM',
                    'description': 'Potential steganography detected in base64 data'
                }
        
        return None
    
    def _analyze_user_agent(self, request):
        """Analyze user agent for bot and attack patterns"""
        ua = request.META.get('HTTP_USER_AGENT', '')
        
        # Known attack tools
        attack_tools = [
            'sqlmap', 'nikto', 'dirb', 'gobuster', 'wfuzz', 'burpsuite',
            'nmap', 'masscan', 'zap', 'w3af', 'skipfish', 'arachni',
            'curl', 'wget', 'python-requests', 'go-http-client'
        ]
        
        for tool in attack_tools:
            if tool.lower() in ua.lower():
                return {
                    'type': 'attack_tool',
                    'severity': 'HIGH',
                    'description': f'Attack tool detected: {tool}'
                }
        
        # Check for suspicious patterns
        if not ua or len(ua) < 10:
            return {
                'type': 'suspicious_ua',
                'severity': 'MEDIUM',
                'description': 'Missing or suspicious user agent'
            }
        
        return None
    
    def _detect_encoding_obfuscation(self, request):
        """Detect various encoding obfuscation techniques"""
        content = request.path + str(request.GET)
        
        # Check for multiple URL encoding
        if '%25' in content:  # Double URL encoding
            return {
                'type': 'encoding_obfuscation',
                'severity': 'HIGH',
                'description': 'Multiple URL encoding detected'
            }
        
        # Check for Unicode obfuscation
        if re.search(r'%u[0-9a-fA-F]{4}', content):
            return {
                'type': 'encoding_obfuscation',
                'severity': 'HIGH',
                'description': 'Unicode encoding obfuscation detected'
            }
        
        return None
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        headers = [
            'HTTP_CF_CONNECTING_IP',
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_REAL_IP',
            'REMOTE_ADDR'
        ]
        
        for header in headers:
            ip = request.META.get(header)
            if ip:
                return ip.split(',')[0].strip()
        
        return '127.0.0.1'
    
    def generate_threat_report(self, threats, request):
        """Generate comprehensive threat report"""
        if not threats:
            return None
        
        ip = self._get_client_ip(request)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'source_ip': ip,
            'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
            'path': request.path,
            'method': request.method,
            'threats': threats,
            'severity': max(threat.get('severity', 'LOW') for threat in threats),
            'threat_count': len(threats),
            'recommended_action': self._get_recommended_action(threats)
        }
        
        # Log the threat
        logger.error(f"Security threat detected: {report}")
        
        return report
    
    def _get_recommended_action(self, threats):
        """Get recommended action based on threat severity"""
        severities = [threat.get('severity', 'LOW') for threat in threats]
        
        if 'CRITICAL' in severities:
            return 'BLOCK_IMMEDIATELY'
        elif 'HIGH' in severities:
            return 'BLOCK_AND_MONITOR'
        elif 'MEDIUM' in severities:
            return 'MONITOR_CLOSELY'
        else:
            return 'LOG_ONLY'

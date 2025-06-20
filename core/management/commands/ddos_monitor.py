from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.conf import settings
import time
import json
from datetime import datetime
from core.ddos_monitor import DDoSMonitor


class Command(BaseCommand):
    help = 'DDoS Protection Monitor for Hyperwave Networks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--monitor',
            action='store_true',
            help='Run continuous monitoring (Ctrl+C to stop)'
        )
        parser.add_argument(
            '--report',
            action='store_true',
            help='Generate security report'
        )
        parser.add_argument(
            '--health',
            action='store_true',
            help='Check system health status'
        )
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Analyze current attack patterns'
        )
        parser.add_argument(
            '--clear-blocks',
            action='store_true',
            help='Clear all blocked IPs (use with caution)'
        )
        parser.add_argument(
            '--emergency-off',
            action='store_true',
            help='Disable emergency mode'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show current protection statistics'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='Monitoring interval in seconds (default: 30)'
        )

    def handle(self, *args, **options):
        monitor = DDoSMonitor()
        
        self.stdout.write(
            self.style.SUCCESS('🛡️  Hyperwave Networks DDoS Protection Monitor')
        )
        self.stdout.write('=' * 60)
        
        if options['monitor']:
            self.run_continuous_monitor(monitor, options['interval'])
        elif options['report']:
            self.generate_report(monitor)
        elif options['health']:
            self.check_health(monitor)
        elif options['analyze']:
            self.analyze_attacks(monitor)
        elif options['clear_blocks']:
            self.clear_blocks()
        elif options['emergency_off']:
            self.disable_emergency_mode()
        elif options['stats']:
            self.show_stats(monitor)
        else:
            self.show_dashboard(monitor)

    def run_continuous_monitor(self, monitor, interval):
        """Run continuous monitoring"""
        self.stdout.write(
            self.style.WARNING(f'Starting continuous monitoring (interval: {interval}s)')
        )
        self.stdout.write('Press Ctrl+C to stop...\n')
        
        try:
            while True:
                self.stdout.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
                
                # Health check
                health = monitor.health_check()
                if health['emergency_mode']:
                    self.stdout.write(
                        self.style.ERROR('🚨 EMERGENCY MODE ACTIVE')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS('✅ System Normal')
                    )
                
                # Show key metrics
                self.stdout.write(f"Requests/min: {health['system_load']['requests_per_minute']}")
                self.stdout.write(f"Blocked IPs: {health['blocked_ips_count']}")
                
                # Check for active attacks
                analysis = monitor.analyze_attack_patterns()
                if analysis['active_attacks']:
                    self.stdout.write(
                        self.style.ERROR(f"⚠️  Active attacks: {len(analysis['active_attacks'])}")
                    )
                    for attack in analysis['active_attacks']:
                        self.stdout.write(f"  - {attack['type']}: {attack['description']}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.stdout.write('\nMonitoring stopped.')

    def generate_report(self, monitor):
        """Generate comprehensive security report"""
        self.stdout.write(
            self.style.HTTP_INFO('📊 Generating Security Report...')
        )
        
        report = monitor.generate_security_report()
        
        self.stdout.write(f"\n{self.style.SUCCESS('Security Report')}")
        self.stdout.write(f"Report ID: {report['report_id']}")
        self.stdout.write(f"Generated: {report['generated_at']}")
        self.stdout.write(f"Period: {report['period']}")
        
        # Summary
        summary = report['summary']
        self.stdout.write(f"\n{self.style.HTTP_INFO('Summary:')}")
        self.stdout.write(f"  Total Requests: {summary['total_requests']:,}")
        self.stdout.write(f"  Blocked Requests: {summary['blocked_requests']:,}")
        self.stdout.write(f"  Unique IPs: {summary['unique_ips']:,}")
        self.stdout.write(f"  Attack Attempts: {summary['attack_attempts']:,}")
        
        # Security Metrics
        metrics = report['security_metrics']
        self.stdout.write(f"\n{self.style.HTTP_INFO('Security Metrics:')}")
        self.stdout.write(f"  Protection Effectiveness: {metrics['ddos_protection_effectiveness']}")
        self.stdout.write(f"  False Positive Rate: {metrics['false_positive_rate']}")
        self.stdout.write(f"  Response Time: {metrics['response_time']}")
        self.stdout.write(f"  Uptime: {metrics['uptime']}")
        
        # Recommendations
        self.stdout.write(f"\n{self.style.HTTP_INFO('Recommendations:')}")
        for rec in report['recommendations']:
            self.stdout.write(f"  • {rec}")

    def check_health(self, monitor):
        """Check system health"""
        health = monitor.health_check()
        
        self.stdout.write(f"{self.style.HTTP_INFO('System Health Check')}")
        self.stdout.write(f"Timestamp: {health['timestamp']}")
        
        # Status indicators
        status_items = [
            ('DDoS Protection', health['ddos_protection']),
            ('Rate Limiting', health['rate_limiting']),
            ('Admin Protection', health['admin_protection']),
        ]
        
        for name, status in status_items:
            if status == 'ACTIVE':
                self.stdout.write(f"✅ {name}: {self.style.SUCCESS(status)}")
            else:
                self.stdout.write(f"❌ {name}: {self.style.ERROR(status)}")
        
        # Emergency mode check
        if health['emergency_mode']:
            self.stdout.write(f"🚨 Emergency Mode: {self.style.ERROR('ACTIVE')}")
        else:
            self.stdout.write(f"✅ Emergency Mode: {self.style.SUCCESS('INACTIVE')}")
        
        # System load
        load = health['system_load']
        self.stdout.write(f"\n{self.style.HTTP_INFO('System Load:')}")
        self.stdout.write(f"  Requests/min: {load['requests_per_minute']}")
        self.stdout.write(f"  Cache Hit Ratio: {load['cache_hit_ratio']}")
        self.stdout.write(f"  Memory Usage: {load['memory_usage']}")
        self.stdout.write(f"  CPU Usage: {load['cpu_usage']}")

    def analyze_attacks(self, monitor):
        """Analyze current attack patterns"""
        analysis = monitor.analyze_attack_patterns()
        
        self.stdout.write(f"{self.style.HTTP_INFO('Attack Pattern Analysis')}")
        
        # Active attacks
        active_attacks = analysis['active_attacks']
        if active_attacks:
            self.stdout.write(f"\n🚨 {self.style.ERROR('Active Attacks:')}")
            for attack in active_attacks:
                severity_style = self.style.ERROR if attack['severity'] == 'CRITICAL' else self.style.WARNING
                self.stdout.write(f"  {severity_style(attack['severity'])}: {attack['type']}")
                self.stdout.write(f"    Description: {attack['description']}")
                self.stdout.write(f"    Mitigation: {attack['mitigation']}")
                if 'source_ip' in attack:
                    self.stdout.write(f"    Source IP: {attack['source_ip']}")
        else:
            self.stdout.write(f"\n✅ {self.style.SUCCESS('No active attacks detected')}")
        
        # Attack types
        attack_types = analysis['attack_types']
        if attack_types:
            self.stdout.write(f"\n{self.style.HTTP_INFO('Attack Types Detected:')}")
            for attack_type, count in attack_types.items():
                self.stdout.write(f"  {attack_type}: {count}")
        
        # Recommendations
        recommendations = analysis['recommendations']
        if recommendations:
            self.stdout.write(f"\n{self.style.HTTP_INFO('Recommendations:')}")
            for rec in recommendations:
                if 'CRITICAL' in rec:
                    self.stdout.write(f"  🚨 {self.style.ERROR(rec)}")
                else:
                    self.stdout.write(f"  • {rec}")

    def clear_blocks(self):
        """Clear all blocked IPs"""
        self.stdout.write(
            self.style.WARNING('⚠️  This will clear ALL blocked IPs!')
        )
        
        confirm = input("Are you sure? Type 'YES' to confirm: ")
        if confirm == 'YES':
            # Clear emergency modes
            cache.delete("emergency_mode")
            cache.delete("admin_emergency_mode")
            cache.delete("high_alert_mode")
            
            # Note: In production, you'd iterate through blocked IP cache keys
            # This is a simplified version
            self.stdout.write(
                self.style.SUCCESS('✅ Cleared emergency modes and restrictions')
            )
            self.stdout.write(
                self.style.WARNING('Note: Individual IP blocks may persist until their TTL expires')
            )
        else:
            self.stdout.write('Operation cancelled.')

    def disable_emergency_mode(self):
        """Disable emergency mode"""
        if cache.get("emergency_mode", False):
            cache.delete("emergency_mode")
            self.stdout.write(
                self.style.SUCCESS('✅ Emergency mode disabled')
            )
        else:
            self.stdout.write(
                self.style.HTTP_INFO('Emergency mode was not active')
            )

    def show_stats(self, monitor):
        """Show current protection statistics"""
        self.stdout.write(f"{self.style.HTTP_INFO('DDoS Protection Statistics')}")
        
        # Current cache statistics
        global_requests = cache.get("global_request_rate", [])
        current_time = time.time()
        recent_requests = [r for r in global_requests if current_time - r < 60]
        
        self.stdout.write(f"Current requests/min: {len(recent_requests)}")
        
        # Check various protection metrics
        emergency_mode = cache.get("emergency_mode", False)
        admin_emergency = cache.get("admin_emergency_mode", False)
        high_alert = cache.get("high_alert_mode", False)
        
        self.stdout.write(f"\n{self.style.HTTP_INFO('Protection Status:')}")
        self.stdout.write(f"  Emergency Mode: {'🚨 ACTIVE' if emergency_mode else '✅ Inactive'}")
        self.stdout.write(f"  Admin Emergency: {'🚨 ACTIVE' if admin_emergency else '✅ Inactive'}")
        self.stdout.write(f"  High Alert: {'⚠️ ACTIVE' if high_alert else '✅ Inactive'}")
        
        # Global stats
        admin_attempts = cache.get("admin_login_attempts:global", 0)
        self.stdout.write(f"\n{self.style.HTTP_INFO('Recent Activity:')}")
        self.stdout.write(f"  Global admin attempts: {admin_attempts}")
        
        if len(recent_requests) > 100:
            self.stdout.write(
                self.style.WARNING(f"⚠️  High traffic detected: {len(recent_requests)} requests/min")
            )
        elif len(recent_requests) > 500:
            self.stdout.write(
                self.style.ERROR(f"🚨 Very high traffic: {len(recent_requests)} requests/min")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Normal traffic: {len(recent_requests)} requests/min")
            )

    def show_dashboard(self, monitor):
        """Show main dashboard"""
        self.stdout.write(f"{self.style.HTTP_INFO('DDoS Protection Dashboard')}")
        
        # Quick health check
        health = monitor.health_check()
        
        if health['emergency_mode']:
            self.stdout.write(f"Status: {self.style.ERROR('🚨 EMERGENCY MODE ACTIVE')}")
        else:
            self.stdout.write(f"Status: {self.style.SUCCESS('✅ System Operational')}")
        
        # Quick stats
        load = health['system_load']
        self.stdout.write(f"Requests/min: {load['requests_per_minute']}")
        self.stdout.write(f"Blocked IPs: {health['blocked_ips_count']}")
        
        # Available commands
        self.stdout.write(f"\n{self.style.HTTP_INFO('Available Commands:')}")
        commands = [
            ('--monitor', 'Start continuous monitoring'),
            ('--health', 'Check system health'),
            ('--analyze', 'Analyze attack patterns'),
            ('--report', 'Generate security report'),
            ('--stats', 'Show protection statistics'),
            ('--emergency-off', 'Disable emergency mode'),
            ('--clear-blocks', 'Clear blocked IPs (caution)')
        ]
        
        for cmd, desc in commands:
            self.stdout.write(f"  {cmd}: {desc}")
        
        self.stdout.write(f"\nExample: python manage.py ddos_monitor --monitor") 
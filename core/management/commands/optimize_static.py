from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
import os
import gzip
import shutil
from pathlib import Path

class Command(BaseCommand):
    help = 'Optimize static files for better performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Compress static files with gzip',
        )
        parser.add_argument(
            '--minify',
            action='store_true',
            help='Minify CSS and JS files',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting static file optimization...'))
        
        # First collect static files
        call_command('collectstatic', '--noinput')
        
        static_root = Path(settings.STATIC_ROOT)
        
        if options['compress']:
            self.compress_files(static_root)
        
        if options['minify']:
            self.minify_files(static_root)
        
        self.stdout.write(self.style.SUCCESS('Static file optimization completed!'))

    def compress_files(self, static_root):
        """Compress static files with gzip"""
        self.stdout.write('Compressing static files...')
        
        compressible_extensions = ['.css', '.js', '.html', '.txt', '.xml', '.json']
        compressed_count = 0
        
        for root, dirs, files in os.walk(static_root):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in compressible_extensions:
                    self.compress_file(file_path)
                    compressed_count += 1
        
        self.stdout.write(f'Compressed {compressed_count} files')

    def compress_file(self, file_path):
        """Compress a single file with gzip"""
        try:
            with open(file_path, 'rb') as f_in:
                with gzip.open(f'{file_path}.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        except Exception as e:
            self.stdout.write(f'Error compressing {file_path}: {e}')

    def minify_files(self, static_root):
        """Basic minification of CSS and JS files"""
        self.stdout.write('Minifying CSS and JS files...')
        
        for root, dirs, files in os.walk(static_root):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix == '.css':
                    self.minify_css(file_path)
                elif file_path.suffix == '.js':
                    self.minify_js(file_path)

    def minify_css(self, file_path):
        """Basic CSS minification"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic minification
            content = content.replace('\n', ' ')
            content = content.replace('\r', ' ')
            content = ' '.join(content.split())  # Remove extra spaces
            content = content.replace('; ', ';')
            content = content.replace(': ', ':')
            content = content.replace('{ ', '{')
            content = content.replace(' }', '}')
            content = content.replace(', ', ',')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            self.stdout.write(f'Error minifying CSS {file_path}: {e}')

    def minify_js(self, file_path):
        """Basic JS minification"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic minification (remove comments and extra whitespace)
            lines = content.split('\n')
            minified_lines = []
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('//') and not line.startswith('/*'):
                    minified_lines.append(line)
            
            content = ' '.join(minified_lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            self.stdout.write(f'Error minifying JS {file_path}: {e}') 
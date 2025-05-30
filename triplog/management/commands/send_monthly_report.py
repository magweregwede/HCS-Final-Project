import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from .generate_trip_report import TripReportGenerator

class Command(BaseCommand):
    help = 'Generate and send monthly trip report via email'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--recipients',
            nargs='+',
            help='Email addresses to send the report to',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force send report regardless of date',
        )
    
    def handle(self, *args, **options):
        try:
            # Generate the report
            generator = TripReportGenerator()
            filepath = generator.generate_comprehensive_report()
            
            self.stdout.write(
                self.style.SUCCESS(f'Report generated: {filepath}')
            )
            
            # Get recipients
            recipients = options.get('recipients') or getattr(settings, 'MONTHLY_REPORT_RECIPIENTS', [])
            
            if not recipients:
                self.stdout.write(
                    self.style.ERROR('No recipients specified. Add them via --recipients or MONTHLY_REPORT_RECIPIENTS setting.')
                )
                return
            
            # Send email - this calls the method from TripReportGenerator
            generator.send_monthly_report_email(filepath, recipients)
            
            self.stdout.write(
                self.style.SUCCESS(f'Email sent successfully to: {", ".join(recipients)}')
            )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )
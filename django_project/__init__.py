import os
import django
from django.conf import settings

# Only start scheduler if Django is fully loaded and in production/development
if os.environ.get('RUN_MAIN') or os.environ.get('WERKZEUG_RUN_MAIN'):
    # This ensures the scheduler only starts once
    if hasattr(settings, 'DATABASES'):  # Check if Django is configured
        try:
            from triplog.scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            print(f"Failed to start scheduler: {e}")
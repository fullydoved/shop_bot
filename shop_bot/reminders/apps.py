import os
import sys
from django.apps import AppConfig


class RemindersConfig(AppConfig):
    name = 'reminders'

    def ready(self):
        """Start the reminder scheduler when Django starts."""
        # Only start scheduler in the main process, not in migrations/shell/etc
        # Check for runserver or gunicorn
        is_runserver = 'runserver' in sys.argv
        is_gunicorn = 'gunicorn' in sys.argv[0] if sys.argv else False

        # Also skip if running migrations, tests, or shell
        skip_commands = {'migrate', 'makemigrations', 'shell', 'test', 'collectstatic'}
        is_management_command = any(cmd in sys.argv for cmd in skip_commands)

        # RUN_MAIN is set by Django's autoreloader to avoid double-starting
        is_main_process = os.environ.get('RUN_MAIN') == 'true'

        if (is_runserver and is_main_process) or is_gunicorn:
            if not is_management_command:
                from .scheduler import start_scheduler
                start_scheduler()

from django.core.management.base import BaseCommand
from cli.main import run_repl


class Command(BaseCommand):
    help = 'Start Beavs - your friendly shop assistant'

    def handle(self, *args, **options):
        run_repl()

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Set up user groups with appropriate permissions'

    def handle(self, *args, **options):
        # Create groups
        clerks_group, created = Group.objects.get_or_create(name='clerks')
        managers_group, created = Group.objects.get_or_create(name='managers')
        drivers_group, created = Group.objects.get_or_create(name='drivers')
        
        self.stdout.write('Groups created successfully!')
        self.stdout.write('Remember to assign users to appropriate groups in Django admin.')
        self.stdout.write('- clerks: Can view logistics partners, full access to deliveries')
        self.stdout.write('- managers: Full access to everything')
        self.stdout.write('- drivers: Can access driver availability and leaderboard')
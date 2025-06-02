from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand
from triplog.models import Driver as TriplogDriver
from drivers.models import DriverAvailability

class Command(BaseCommand):
    help = 'Set up initial driver availability records'

    def handle(self, *args, **options):
        # Create groups if they don't exist
        clerks_group, created = Group.objects.get_or_create(name='clerks')
        drivers_group, created = Group.objects.get_or_create(name='drivers')
        
        self.stdout.write('Setting up driver availability records...')
        
        # Get all triplog drivers
        triplog_drivers = TriplogDriver.objects.all()
        
        for driver in triplog_drivers:
            # Create username: first letter of first name + all of surname
            name_parts = driver.name.strip().split()
            if len(name_parts) >= 2:
                first_name = name_parts[0]
                surname = name_parts[-1]  # Get the last part as surname
                username = (first_name[0] + surname).lower()
            else:
                # Fallback for single names
                username = driver.name.lower().replace(' ', '').replace('.', '')[:10]
            
            # Remove any special characters and limit length
            username = ''.join(c for c in username if c.isalnum())[:15]
            
            # Handle potential duplicate usernames by adding a number
            original_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            # Create user if doesn't exist
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': name_parts[0] if name_parts else '',
                    'last_name': ' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
                    'email': f'{username}@company.com',
                }
            )
            
            if user_created:
                user.set_password('defaultpassword123')  # Set a default password
                user.save()
                drivers_group.user_set.add(user)
                self.stdout.write(f'Created user: {username} for driver: {driver.name}')
            
            # Create availability record if doesn't exist
            availability, av_created = DriverAvailability.objects.get_or_create(
                user=user,
                triplog_driver=driver,
                defaults={'is_available': True}
            )
            
            if av_created:
                self.stdout.write(f'Created availability record for: {driver.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up driver availability records!')
        )
        self.stdout.write('Default password for new users: defaultpassword123')
        self.stdout.write('Remember to create clerk users and add them to the "clerks" group.')
        
        # Display username mapping
        self.stdout.write('\nUsername mapping:')
        for availability in DriverAvailability.objects.all():
            self.stdout.write(f'{availability.triplog_driver.name} -> {availability.user.username}')
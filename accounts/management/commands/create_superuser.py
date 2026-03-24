"""Management command to create/update superuser."""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os
import secrets
import string

class Command(BaseCommand):
    help = 'Create or update superuser'

    def handle(self, *args, **options):
        User = get_user_model()
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@elitewealthcapita.uk')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
        
        # Generate secure random password if not provided
        if not password:
            alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
            password = ''.join(secrets.choice(alphabet) for _ in range(16))
            self.stdout.write(self.style.WARNING(f'Generated password: {password}'))
            self.stdout.write(self.style.WARNING('Set DJANGO_SUPERUSER_PASSWORD env var in production!'))
        
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated superuser: {email}'))
        else:
            User.objects.create_superuser(email=email, password=password, full_name='Elite Admin')
            self.stdout.write(self.style.SUCCESS(f'Created superuser: {email}'))

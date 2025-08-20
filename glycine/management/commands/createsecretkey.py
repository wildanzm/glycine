from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Generates a new secret key and updates the .env file.'

    def handle(self, *args, **options):
        secret_key = get_random_secret_key()
        
        env_path = os.path.join(settings.BASE_DIR, '.env')
        
        try:
            with open(env_path, 'r') as f:
                lines = f.readlines()

            key_exists = False
            for i, line in enumerate(lines):
                if line.startswith('SECRET_KEY='):
                    lines[i] = f'SECRET_KEY={secret_key}\n'
                    key_exists = True
                    break
            
            if not key_exists:
                lines.append(f'\nSECRET_KEY={secret_key}\n')

            with open(env_path, 'w') as f:
                f.writelines(lines)
            
            self.stdout.write(self.style.SUCCESS(f'Successfully generated and updated SECRET_KEY in {env_path}'))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'.env file not found at {env_path}. Please create one.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An error occurred: {e}'))
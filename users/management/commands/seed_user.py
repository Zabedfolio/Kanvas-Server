import bcrypt
import uuid
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from users.models import BetterAuthUser, BetterAuthAccount

class Command(BaseCommand):
    help = 'Seeds a demo user and account compatible with Better Auth'

    def handle(self, *args, **options):
        email = 'demo@example.com'
        password = 'password123'

        self.stdout.write(f"Seeding user: {email} with password: {password}...")

        try:
            with transaction.atomic():
                # 1. Create or get the User record
                user, user_created = BetterAuthUser.objects.get_or_create(
                    email=email,
                    defaults={
                        'id': str(uuid.uuid4()),
                        'name': 'Demo User',
                        'email_verified': True,
                        'created_at': timezone.now(),
                        'updated_at': timezone.now(),
                    }
                )

                if not user_created:
                    self.stdout.write(self.style.SUCCESS(f"User {email} already exists."))
                else:
                    self.stdout.write(self.style.SUCCESS(f"User {email} created."))

                # 2. Generate bcrypt hash for the password
                # Better Auth expects a standard bcrypt hash
                hashed_password = bcrypt.hashpw(
                    password.encode('utf-8'), 
                    bcrypt.gensalt(rounds=10)
                ).decode('utf-8')

                # 3. Create or update the Account record for credentials provider
                account, account_created = BetterAuthAccount.objects.get_or_create(
                    user=user,
                    provider_id='credential',
                    defaults={
                        'id': str(uuid.uuid4()),
                        'account_id': email,
                        'password': hashed_password,
                        'created_at': timezone.now(),
                        'updated_at': timezone.now(),
                    }
                )

                if not account_created:
                    account.password = hashed_password
                    account.updated_at = timezone.now()
                    account.save()
                    self.stdout.write(self.style.SUCCESS("Account password updated."))
                else:
                    self.stdout.write(self.style.SUCCESS("Account credential created."))

                self.stdout.write(self.style.SUCCESS("Successfully seeded demo credentials!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding user: {e}"))

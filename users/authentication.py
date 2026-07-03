from django.utils import timezone
from rest_framework import authentication
from rest_framework import exceptions
from .models import BetterAuthSession

class BetterAuthDRFAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # 1. Read token from cookie
        token = request.COOKIES.get('better-auth.session_token')
        
        # 2. Fallback to Authorization header
        if not token:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return None

        # 3. Clean token (Better Auth cookies contain signature: token.signature)
        if '.' in token:
            token = token.split('.')[0]

        try:
            # Query session and join user
            session = BetterAuthSession.objects.select_related('user').get(token=token)
        except BetterAuthSession.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid or expired session token')

        # 3. Expiration validation (safe timezone comparison)
        now = timezone.now()
        if timezone.is_naive(session.expires_at):
            now = timezone.make_naive(now)

        if session.expires_at < now:
            # Clean up expired session if we want, or just fail
            raise exceptions.AuthenticationFailed('Session has expired')

        # Check if user is active
        if not session.user.is_active:
            raise exceptions.AuthenticationFailed('User is inactive')

        return (session.user, session)

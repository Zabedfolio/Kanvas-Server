from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class BetterAuthUserManager(BaseUserManager):
    def create_user(self, email, name=None, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra_fields)

class BetterAuthUser(AbstractBaseUser):
    # Better Auth user schema compatibility
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False, db_column='emailVerified')
    image = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(db_column='createdAt', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updatedAt', auto_now=True)
    
    # Required django fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # We do not use password in User table directly for Better Auth (it uses Account),
    # but AbstractBaseUser requires it. We make it nullable.
    password = models.CharField(max_length=128, null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = BetterAuthUserManager()
    
    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class BetterAuthSession(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    expires_at = models.DateTimeField(db_column='expiresAt')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(db_column='createdAt')
    updated_at = models.DateTimeField(db_column='updatedAt')
    user = models.ForeignKey(BetterAuthUser, on_delete=models.CASCADE, db_column='userId')
    ip_address = models.CharField(max_length=255, null=True, blank=True, db_column='ipAddress')
    user_agent = models.TextField(null=True, db_column='userAgent', blank=True)

    class Meta:
        db_table = 'session'

    def __str__(self):
        return f"Session for {self.user.email} (expires {self.expires_at})"


class BetterAuthAccount(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    account_id = models.CharField(max_length=255, db_column='accountId')
    provider_id = models.CharField(max_length=255, db_column='providerId')
    user = models.ForeignKey(BetterAuthUser, on_delete=models.CASCADE, db_column='userId')
    access_token = models.TextField(null=True, blank=True, db_column='accessToken')
    refresh_token = models.TextField(null=True, blank=True, db_column='refreshToken')
    id_token = models.TextField(null=True, blank=True, db_column='idToken')
    expires_at = models.DateTimeField(null=True, blank=True, db_column='expiresAt')
    password = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(db_column='createdAt')
    updated_at = models.DateTimeField(db_column='updatedAt')

    class Meta:
        db_table = 'account'

    def __str__(self):
        return f"Account {self.provider_id} for {self.user.email}"


class BetterAuthVerification(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    identifier = models.TextField()
    value = models.TextField()
    expires_at = models.DateTimeField(db_column='expiresAt')
    created_at = models.DateTimeField(db_column='createdAt', null=True, blank=True)
    updated_at = models.DateTimeField(db_column='updatedAt', null=True, blank=True)

    class Meta:
        db_table = 'verification'

    def __str__(self):
        return f"Verification for {self.identifier}"


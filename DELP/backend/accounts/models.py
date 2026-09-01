from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    # Use email as the primary identifier instead of username
    username = None
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(_('full name'), max_length=255, blank=True)
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_verified = models.BooleanField(_('verified'), default=False)

    # Role-based permissions
    ROLE_CHOICES = [
        ('hm', 'Headmaster'),
        ('meo', 'Mandal Education Officer'),
        ('deo', 'District Education Officer'),
        ('state_official', 'State Education Department Official'),
        ('admin', 'Platform Admin'),
    ]
    role = models.CharField(_('role'), max_length=20, choices=ROLE_CHOICES, default='hm')

    # Audit fields
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name() or self.email} ({self.get_role_display()})"

    def get_full_name(self):
        return self.name or super().get_full_name()

    def has_role(self, role):
        return self.role == role

    def is_headmaster(self):
        return self.has_role('hm')

    def is_meo(self):
        return self.has_role('meo')

    def is_admin(self):
        return self.has_role('admin')

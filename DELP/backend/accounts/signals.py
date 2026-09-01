from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_related_profiles(sender, instance, created, **kwargs):
    """
    Hook for any role-specific profile auto-creation when a User is created.
    In Phase 1, role-specific profiles (Headmaster, MEO, etc.) are created
    explicitly by the admin or via API after a User is created. This signal
    is a placeholder for future automation (e.g., deo_profile auto-create).
    """
    if not created:
        return
    # Intentionally a no-op for now; future hooks can branch on instance.role.
    return

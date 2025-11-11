from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Profile, Role, User, UserSession


# type: ignore is used because the linter may not recognize the dynamic 'through' attribute on ManyToManyField
@receiver(m2m_changed, sender=User.roles.through)  # type: ignore
def sync_is_staff_with_admin_role(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        admin_role = Role.objects.filter(name="admin").first()
        if admin_role and instance.roles.filter(pk=admin_role.pk).exists():
            if not instance.is_staff:
                instance.is_staff = True
                instance.save(update_fields=["is_staff"])
        else:
            if instance.is_staff:
                instance.is_staff = False
                instance.save(update_fields=["is_staff"])


@receiver(user_logged_in)
def create_user_session(sender, request, user, **kwargs):
    """Create a UserSession record when a user logs in."""
    try:
        # Ensure session key exists
        if not request.session.session_key:
            request.session.save()

        session_key = request.session.session_key

        # Check if session already exists
        existing_session = UserSession.objects.filter(
            user=user,
            session_key=session_key,
            is_active=True
        ).first()

        if existing_session:
            # Update last activity
            existing_session.last_activity = timezone.now()
            existing_session.save()
        else:
            # Create new session record
            UserSession.objects.create(
                user=user,
                session_key=session_key,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=request.META.get('REMOTE_ADDR'),
                device=get_device_info(request.META.get('HTTP_USER_AGENT', '')),
                location=get_location_info(request.META.get('REMOTE_ADDR')),
                is_active=True
            )
    except Exception as e:
        # Log error but don't break the login process
        print(f"Error creating user session: {e}")


def get_device_info(user_agent):
    """Extract device information from user agent."""
    if not user_agent:
        return 'Unknown'

    user_agent_lower = user_agent.lower()
    if 'mobile' in user_agent_lower or 'android' in user_agent_lower or 'iphone' in user_agent_lower:
        return 'Mobile'
    elif 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
        return 'Tablet'
    else:
        return 'Desktop'


def get_location_info(ip_address):
    """Get location information from IP address (simplified)."""
    if not ip_address:
        return 'Unknown'

    # For now, just return a generic location
    # In production, you might use a geolocation service
    if ip_address in ['127.0.0.1', 'localhost']:
        return 'Local'
    else:
        return 'Remote'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile for new users."""
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the user's profile when the user is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()

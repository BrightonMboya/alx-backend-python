from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    """
    Signal handler to create a notification when a new message is created
    """
    if created:  # Only create notification for new messages
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )
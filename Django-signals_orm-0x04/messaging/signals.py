from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory
from django.utils import timezone
from django.contrib.auth.models import User


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

@receiver(pre_save, sender=Message)
def track_message_history(sender, instance, **kwargs):
    """
    Signal handler to track message edit history before saving changes
    """
    if instance.pk:  # Only for existing messages (not new ones)
        try:
            old_message = Message.objects.get(pk=instance.pk)
            # Only create history if content changed
            if old_message.content != instance.content:
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=instance.sender
                )
                instance.edited = True
                instance.last_edited = timezone.now()
        except Message.DoesNotExist:
            pass


@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Signal handler to clean up all related data when a user is deleted.
    Note: Most deletions will be handled by CASCADE, this is a backup.
    """
    # Clean up any remaining messages
    Message.objects.filter(
        sender=instance
    ).delete()
    Message.objects.filter(
        receiver=instance
    ).delete()
    
    # Clean up any remaining notifications
    Notification.objects.filter(
        user=instance
    ).delete()
    
    # Clean up any remaining message histories
    MessageHistory.objects.filter(
        edited_by=instance
    ).delete()
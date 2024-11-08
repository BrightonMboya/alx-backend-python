from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory
from django.utils import timezone

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
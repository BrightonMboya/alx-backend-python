from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey

class Message(models.Model):
    sender = models.ForeignKey(
        User, 
        related_name='sent_messages',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User,
        related_name='received_messages',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)
    
    # Managers
    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # Custom manager for unread messages
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"From {self.sender} to {self.receiver} at {self.timestamp}"
    
    def mark_as_read(self):
        """Mark individual message as read"""
        if not self.read:
            self.read = True
            self.save(update_fields=['read'])
    
class MessageHistory(models.Model):
    message = models.ForeignKey(
        Message,
        related_name='history',
        on_delete=models.CASCADE  # Will delete history when message is deleted
    )
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # Keep history but set user to NULL when deleted
        null=True
    )
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(
        User,
        related_name='notifications',
        on_delete=models.CASCADE  # Will delete notifications when user is deleted
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE  # Will delete notifications when message is deleted
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

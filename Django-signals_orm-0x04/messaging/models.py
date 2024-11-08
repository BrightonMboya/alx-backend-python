from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey

class Message(MPTTModel):
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
    is_read = models.BooleanField(default=False)
    parent_message = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    class MPTTMeta:
        order_insertion_by = ['timestamp']
    
    class Meta:
        ordering = ['tree_id', 'lft']
    
    def __str__(self):
        return f"From {self.sender} to {self.receiver} at {self.timestamp}"
    
    @property
    def thread_id(self):
        """Return the ID of the root message in this thread"""
        return self.get_root().id
    
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

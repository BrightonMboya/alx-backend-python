from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
    is_read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)
    last_edited = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"From {self.sender} to {self.receiver} at {self.timestamp}"
    
class MessageHistory(models.Model):
    message = models.ForeignKey(
        Message,
        related_name='history',
        on_delete=models.CASCADE
    )
    old_content = models.TextField()
    edited_at = models.DateTimeField(default=timezone.now)
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = 'Message histories'

    def __str__(self):
        return f"Edit history for message {self.message.id} at {self.edited_at}"

class Notification(models.Model):
    user = models.ForeignKey(
        User,
        related_name='notifications',
        on_delete=models.CASCADE
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Notification for {self.user} - Message from {self.message.sender}"

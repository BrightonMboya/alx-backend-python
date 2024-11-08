from django.db import models
from django.db.models import Q

class MessageQuerySet(models.QuerySet):
    def unread(self):
        """Filter for unread messages only"""
        return self.filter(read=False)
    
    def for_user(self, user):
        """Filter messages for a specific user (both sent and received)"""
        return self.filter(Q(receiver=user) | Q(sender=user))
    
    def received_by(self, user):
        """Filter messages received by a specific user"""
        return self.filter(receiver=user)
    
    def sent_by(self, user):
        """Filter messages sent by a specific user"""
        return self.filter(sender=user)

class UnreadMessagesManager(models.Manager):
    def get_queryset(self):
        return MessageQuerySet(self.model, using=self._db)
    
    def unread_for_user(self, user):
        """Get all unread messages for a specific user"""
        return self.get_queryset().unread().received_by(user).only(
            'sender__username',
            'content',
            'timestamp',
            'read'
        ).select_related('sender')
    
    def mark_as_read(self, message_ids, user):
        """Mark specific messages as read for a user"""
        return self.get_queryset().filter(
            id__in=message_ids,
            receiver=user,
            read=False
        ).update(read=True)
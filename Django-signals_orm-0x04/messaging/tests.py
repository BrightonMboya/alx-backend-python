from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification

class MessagingTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='test123')
        self.receiver = User.objects.create_user(username='receiver', password='test123')

    def test_message_creation(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.receiver, self.receiver)
        self.assertFalse(message.is_read)

    def test_notification_creation(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        # Test if notification was automatically created by the signal
        notification = Notification.objects.filter(
            user=self.receiver,
            message=message
        ).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.receiver)
        self.assertFalse(notification.is_read)
from django_filters import rest_framework as filters
from .models import Message, Conversation

class MessageFilter(filters.FilterSet):
    start_date = filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    end_date = filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    sender = filters.UUIDFilter(field_name='sender__user_id')
    message_body = filters.CharFilter(field_name='message_body', lookup_expr='icontains')

    class Meta:
        model = Message
        fields = ['start_date', 'end_date', 'sender', 'message_body']

class ConversationFilter(filters.FilterSet):
    participant = filters.UUIDFilter(field_name='participants__user_id')
    start_date = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    end_date = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Conversation
        fields = ['participant', 'start_date', 'end_date']
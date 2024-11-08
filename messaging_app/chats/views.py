from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsConversationParticipant, IsMessageParticipant
from .models import Conversation, Message
from .serializers import ConversationListSerializer, ConversationDetailSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsConversationParticipant]
    serializer_class = ConversationListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['participants__first_name', 'participants__last_name', 'participants__email']

    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationListSerializer

class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsMessageParticipant]
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(
            conversation_id=self.kwargs.get('conversation_pk')
        ).order_by('sent_at')
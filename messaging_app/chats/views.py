from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Conversation, Message, User

from .serializers import (
    ConversationListSerializer,
    ConversationDetailSerializer,
    MessageSerializer
)

class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['participants__first_name', 'participants__last_name', 'participants__email']

    def get_queryset(self):
        """Return conversations where the current user is a participant"""
        return Conversation.objects.filter(
            participants=self.request.user
        ).order_by('-created_at')

    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationListSerializer

    def create(self, request, *args, **kwargs):
        """Create a new conversation"""
        participants_ids = request.data.get('participants', [])
        
        # Add the current user to participants if not included
        if str(request.user.user_id) not in participants_ids:
            participants_ids.append(str(request.user.user_id))
        
        # Validate participants exist
        try:
            participants = User.objects.filter(user_id__in=participants_ids)
            if participants.count() != len(participants_ids):
                return Response(
                    {"error": "One or more participants not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if conversation already exists with these participants
        existing_conversation = None
        user_conversations = Conversation.objects.filter(participants=request.user)
        
        for conv in user_conversations:
            if set(conv.participants.values_list('user_id', flat=True)) == set(participants_ids):
                existing_conversation = conv
                break

        if existing_conversation:
            serializer = self.get_serializer(existing_conversation)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Create new conversation
        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        """Return messages for a specific conversation"""
        conversation_id = self.kwargs.get('conversation_pk')
        return Message.objects.filter(
            conversation_id=conversation_id
        ).order_by('sent_at')

    def create(self, request, *args, **kwargs):
        """Create a new message in the conversation"""
        conversation_id = self.kwargs.get('conversation_pk')
        
        # Verify conversation exists and user is a participant
        try:
            conversation = Conversation.objects.get(
                conversation_id=conversation_id,
                participants=request.user
            )
        except Conversation.DoesNotExist:
            return Response(
                {"error": "Conversation not found or you're not a participant"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Create message
        message_data = {
            'conversation': conversation.conversation_id,
            'sender': request.user.user_id,
            'message_body': request.data.get('message_body')
        }

        serializer = self.get_serializer(data=message_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
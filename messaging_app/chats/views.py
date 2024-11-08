from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Conversation, Message, User
from .serializers import (
    ConversationListSerializer,
    ConversationDetailSerializer,
    MessageSerializer
)
from .permissions import IsParticipantOfConversation, MessagePermission

class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    serializer_class = ConversationListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['participants__first_name', 'participants__last_name', 'participants__email']

    def get_queryset(self):
        """Return only conversations where the user is a participant"""
        return Conversation.objects.filter(
            participants=self.request.user
        ).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationListSerializer

    def create(self, request, *args, **kwargs):
        """Create a new conversation and validate participants"""
        participants_ids = request.data.get('participants', [])
        
        # Ensure current user is included in participants
        if str(request.user.user_id) not in participants_ids:
            participants_ids.append(str(request.user.user_id))
        
        # Validate participants exist
        participants = User.objects.filter(user_id__in=participants_ids)
        if participants.count() != len(participants_ids):
            return Response(
                {"error": "One or more participants not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create conversation and add participants
        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Only allow deletion if user is a participant"""
        conversation = self.get_object()
        if request.user not in conversation.participants.all():
            return Response(
                {"error": "You don't have permission to delete this conversation"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsParticipantOfConversation, MessagePermission]
    serializer_class = MessageSerializer

    def get_queryset(self):
        """Return messages for a specific conversation"""
        conversation_id = self.kwargs.get('conversation_pk')
        return Message.objects.filter(
            conversation_id=conversation_id
        ).select_related('sender').order_by('sent_at')

    def create(self, request, *args, **kwargs):
        """Create a new message in the conversation"""
        conversation_id = self.kwargs.get('conversation_pk')
        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        
        # Verify user is a participant
        if request.user not in conversation.participants.all():
            return Response(
                {"error": "You are not a participant in this conversation"},
                status=status.HTTP_403_FORBIDDEN
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
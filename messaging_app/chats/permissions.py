from rest_framework import permissions

class IsConversationParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to view or modify it
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        return request.user in obj.participants.all()

class IsMessageParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to view or send messages
    """
    def has_permission(self, request, view):
        conversation_id = view.kwargs.get('conversation_pk')
        if conversation_id:
            return request.user.conversations.filter(
                conversation_id=conversation_id
            ).exists()
        return False

    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        return request.user in obj.conversation.participants.all()
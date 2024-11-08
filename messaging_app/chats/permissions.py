from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission class to ensure only conversation participants can access or modify the conversation
    and its messages.
    """
    
    def has_permission(self, request, view):
        # Allow access to list/create conversations for authenticated users
        if not request.user.is_authenticated:
            return False

        # For create conversation, we don't need to check participation
        if view.action == 'create':
            return True
            
        # For nested message viewset, check conversation participation
        conversation_id = view.kwargs.get('conversation_pk')
        if conversation_id:
            return request.user.conversations.filter(
                conversation_id=conversation_id
            ).exists()
            
        return True

    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant in the conversation
        if hasattr(obj, 'conversation'):  # For Message objects
            return request.user in obj.conversation.participants.all()
        else:  # For Conversation objects
            return request.user in obj.participants.all()


class MessagePermission(permissions.BasePermission):
    """
    Additional permissions specific to messages
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        conversation_id = view.kwargs.get('conversation_pk')
        if not conversation_id:
            return False
            
        # Check if user is part of the conversation
        return request.user.conversations.filter(
            conversation_id=conversation_id
        ).exists()

    def has_object_permission(self, request, view, obj):
        # For update/delete, only allow the sender to modify their own messages
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.sender == request.user
            
        # For read operations, allow all conversation participants
        return request.user in obj.conversation.participants.all()
from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Class-based view URL
    path(
        'conversations/<int:conversation_id>/messages/',
        views.MessageListView.as_view(),
        name='message_list_cbv'
    ),
    # Function-based view URL
    path(
        'conversations/<int:conversation_id>/messages/func/',
        views.message_list,
        name='message_list'
    ),
    # Manual cache view URL
    path(
        'conversations/<int:conversation_id>/messages/manual/',
        views.message_list_manual_cache,
        name='message_list_manual'
    ),
]
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.core.cache import cache
from django.conf import settings
from .models import Message

class MessageListView(ListView):
    model = Message
    template_name = 'messaging/message_list.html'
    context_object_name = 'messages'
    paginate_by = 20

    @method_decorator(cache_page(60))  # Cache for 60 seconds
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def get_queryset(self):
        return (
            Message.objects.filter(
                conversation_id=self.kwargs['conversation_id']
            )
            .select_related('sender', 'receiver')
            .order_by('-timestamp')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add conversation details
        context['conversation_id'] = self.kwargs['conversation_id']
        return context

# Alternative function-based view with caching
@login_required
@cache_page(60)  # Cache for 60 seconds
def message_list(request, conversation_id):
    messages = (
        Message.objects.filter(conversation_id=conversation_id)
        .select_related('sender', 'receiver')
        .order_by('-timestamp')
    )
    return render(request, 'messaging/message_list.html', {
        'messages': messages,
        'conversation_id': conversation_id
    })

# Custom cache key function
def make_message_cache_key(conversation_id, user_id, page=1):
    """Generate a unique cache key for message lists"""
    return f'message_list_{conversation_id}_{user_id}_page_{page}'

# View with manual cache control
@login_required
def message_list_manual_cache(request, conversation_id):
    page = request.GET.get('page', 1)
    cache_key = make_message_cache_key(conversation_id, request.user.id, page)
    
    # Try to get data from cache
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return render(request, 'messaging/message_list.html', cached_data)
    
    # If not in cache, get from database
    messages = (
        Message.objects.filter(conversation_id=conversation_id)
        .select_related('sender', 'receiver')
        .order_by('-timestamp')
    )
    
    context = {
        'messages': messages,
        'conversation_id': conversation_id
    }
    
    # Store in cache for 60 seconds
    cache.set(cache_key, context, 60)
    
    return render(request, 'messaging/message_list.html', context)
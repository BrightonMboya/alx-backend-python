from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.http import require_POST

@login_required
def delete_account_confirmation(request):
    """Display confirmation page for account deletion"""
    return render(request, 'messaging/delete_account.html')

@login_required
@require_POST
def delete_user(request):
    """Handle user account deletion"""
    user = request.user
    # Logout the user first
    logout(request)
    # Delete the user (signals will handle related data cleanup)
    user.delete()
    messages.success(request, 'Your account has been successfully deleted.')
    return redirect('home')

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Prefetch
from .models import Message
from .forms import MessageForm

@login_required
def conversation_list(request):
    """Display list of unique conversations"""
    # Get root messages (messages without parents) for the user
    conversations = Message.objects.root_nodes().filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related('sender', 'receiver').order_by('-timestamp')
    
    return render(request, 'messaging/conversation_list.html', {
        'conversations': conversations
    })

@login_required
def conversation_detail(request, message_id):
    """Display a threaded conversation"""
    root_message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver'),
        id=message_id
    )
    
    # Get all messages in the thread
    thread_messages = (
        Message.objects.filter(tree_id=root_message.tree_id)
        .select_related('sender', 'receiver')
        .order_by('tree_id', 'lft')
    )
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.sender = request.user
            reply.receiver = (
                root_message.sender 
                if root_message.sender != request.user 
                else root_message.receiver
            )
            reply.parent = root_message
            reply.save()
            return redirect('messaging:conversation_detail', message_id=message_id)
    else:
        form = MessageForm()
    
    return render(request, 'messaging/conversation_detail.html', {
        'root_message': root_message,
        'thread_messages': thread_messages,
        'form': form
    })


@login_required
def inbox(request):
    """Display user's inbox with unread messages highlighted"""
    # Get unread messages using the custom manager
    unread_messages = Message.unread.unread_for_user(request.user)
    
    # Get all messages with read status
    all_messages = (
        Message.objects.filter(receiver=request.user)
        .select_related('sender')
        .only(
            'sender__username',
            'content',
            'timestamp',
            'read'
        )
        .order_by('-timestamp')
    )
    
    # Get unread count
    unread_count = unread_messages.count()
    
    return render(request, 'messaging/inbox.html', {
        'unread_messages': unread_messages,
        'all_messages': all_messages,
        'unread_count': unread_count,
    })

@login_required
def mark_messages_read(request):
    """Mark selected messages as read"""
    if request.method == 'POST':
        message_ids = request.POST.getlist('message_ids[]')
        Message.unread.mark_as_read(message_ids, request.user)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
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
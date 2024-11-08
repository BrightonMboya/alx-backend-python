
# Register your models here.
from django.contrib import admin
from .models import Message, Notification, MessageHistory

class MessageHistoryInline(admin.TabularInline):
    model = MessageHistory
    readonly_fields = ('edited_at', 'edited_by', 'old_content')
    extra = 0
    can_delete = False
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp', 'is_read', 'edited', 'last_edited')
    list_filter = ('is_read', 'edited', 'timestamp')
    search_fields = ('sender__username', 'receiver__username', 'content')
    inlines = [MessageHistoryInline]

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('user__username',)
@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('message', 'edited_by', 'edited_at')
    list_filter = ('edited_at', 'edited_by')
    search_fields = ('message__content', 'old_content')
    readonly_fields = ('message', 'edited_at', 'edited_by', 'old_content')
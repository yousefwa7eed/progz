from django.contrib import admin
from .models import Communication

@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ('communication_type', 'direction', 'subject', 'recipient', 'sender', 'status', 'sent_at')
    list_filter = ('communication_type', 'direction', 'status', 'sent_at')
    search_fields = ('subject', 'content', 'recipient')

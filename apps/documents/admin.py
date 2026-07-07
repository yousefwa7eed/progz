from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'document_type', 'related_model', 'uploaded_by', 'created_at')
    list_filter = ('document_type', 'related_model', 'is_confidential')
    search_fields = ('code', 'title', 'notes')
    readonly_fields = ('code', 'file_size', 'created_at')

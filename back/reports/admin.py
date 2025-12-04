from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['type', 'reported_by', 'status', 'created_at', 'reviewed_by']
    list_filter = ['type', 'status', 'created_at']
    search_fields = ['reason', 'reported_by__email', 'action_taken']
    readonly_fields = ['created_at', 'reviewed_at']

from django.contrib import admin

from attendance.models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'status', 'marked_by')
    list_filter = ('status', 'subject', 'date')
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
    date_hierarchy = 'date'

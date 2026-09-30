from django.contrib import admin

from assignments.models import Assignment, AssignmentSubmission


class SubmissionInline(admin.TabularInline):
    model = AssignmentSubmission
    extra = 0


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'section', 'created_by', 'due_date')
    list_filter = ('subject', 'section')
    search_fields = ('title',)
    inlines = [SubmissionInline]


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'is_graded', 'grade')
    list_filter = ('is_graded',)

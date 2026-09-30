from django.contrib import admin

from results.models import Exam, Result


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_class', 'date')
    list_filter = ('school_class',)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'subject', 'marks_obtained', 'max_marks', 'graded_by')
    list_filter = ('exam', 'subject')
    search_fields = ('student__username', 'student__first_name', 'student__last_name')

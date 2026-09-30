from django.contrib import admin

from academics.models import SchoolClass, Section, Subject, TeacherSubjectAssignment


class SectionInline(admin.TabularInline):
    model = Section
    extra = 1


class SubjectInline(admin.TabularInline):
    model = Subject
    extra = 1


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [SectionInline, SubjectInline]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'name', 'class_teacher')
    list_filter = ('school_class',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'school_class')
    list_filter = ('school_class',)
    search_fields = ('name', 'code')


@admin.register(TeacherSubjectAssignment)
class TeacherSubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'section')
    list_filter = ('section__school_class', 'subject')

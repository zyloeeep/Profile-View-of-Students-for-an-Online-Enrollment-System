from django.contrib import admin
from .models import Enrollment, Program, StudentDocument


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("code", "name")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "program", "year_level", "academic_year", "semester", "status")
    list_filter = ("status", "program", "semester")


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ("student", "document_type", "status", "date_submitted")
    list_filter = ("status", "document_type")
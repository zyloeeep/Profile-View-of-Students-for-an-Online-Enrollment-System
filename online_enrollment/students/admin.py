from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "last_name", "first_name", "middle_name", "gender", "email")
    search_fields = ("student_id", "last_name", "first_name")
    list_filter = ("gender",)
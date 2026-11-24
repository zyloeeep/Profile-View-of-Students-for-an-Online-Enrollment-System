from django.db import models
from students.models import Student

class Program(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=150)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code


class Enrollment(models.Model):
    """One row each time a student enrolls in a term, so the history is kept."""

    YEAR_LEVEL_CHOICES = [
        ("1st Year", "1st Year"),
        ("2nd Year", "2nd Year"),
        ("3rd Year", "3rd Year"),
        ("4th Year", "4th Year"),
    ]

    SEMESTER_CHOICES = [
        ("1st", "1st Semester"),
        ("2nd", "2nd Semester"),
        ("Summer", "Summer"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Enrolled", "Enrolled"),
        ("Dropped", "Dropped"),
    ]
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="enrollments"
    )
    program = models.ForeignKey(
        Program, on_delete=models.PROTECT, related_name="enrollments"
    )
    year_level = models.CharField(max_length=10, choices=YEAR_LEVEL_CHOICES)
    section = models.CharField(max_length=20, blank=True)
    academic_year = models.CharField(max_length=9)  # e.g. 2026-2027
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")

    class Meta:
        ordering = ["-enrollment_date", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "academic_year", "semester"],
                name="unique_enrollment_per_term",
            )
        ]

    def __str__(self):
        return f"{self.student.student_id} - {self.program.code} ({self.academic_year}, {self.semester})"


class StudentDocument(models.Model):
    """One row per required document for each student."""

    DOCUMENT_TYPE_CHOICES = [
        ("Birth certificate", "Birth certificate"),
        ("Form 138 / Report card", "Form 138 / Report card"),
        ("Good moral certificate", "Good moral certificate"),
        ("Other", "Other"),
    ]

    STATUS_CHOICES = [
        ("Submitted", "Submitted"),
        ("Missing", "Missing"),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="documents"
    )
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Missing")
    date_submitted = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.student_id} - {self.document_type} ({self.status})"
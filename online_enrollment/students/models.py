from datetime import date
from django.conf import settings
from django.db import models

class Student(models.Model):
    GENDER_CHOICES = [
        ("Female", "Female"),
        ("Male", "Male"),
    ]

    CIVIL_STATUS_CHOICES = [
        ("Single", "Single"),
        ("Married", "Married"),
        ("Widowed", "Widowed"),
        ("Separated", "Separated"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="student_profile",
    )

    # --- Personal ---
    student_id = models.CharField(max_length=20, unique=True)  # e.g. 2026-0101
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    civil_status = models.CharField(max_length=20, choices=CIVIL_STATUS_CHOICES)
    nationality = models.CharField(max_length=50, default="Filipino")
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()

    # --- Family ---
    father_name = models.CharField(max_length=150, blank=True)
    mother_name = models.CharField(max_length=150, blank=True)
    guardian_name = models.CharField(max_length=150, blank=True)
    guardian_contact = models.CharField(max_length=20, blank=True)
    guardian_occupation = models.CharField(max_length=100, blank=True)
    emergency_contact = models.CharField(max_length=200, blank=True)  # name and number

    # --- Education ---
    previous_school = models.CharField(max_length=200, blank=True)
    school_address = models.CharField(max_length=255, blank=True)
    previous_year_level = models.CharField(max_length=50, blank=True)
    school_year = models.CharField(max_length=20, blank=True)
    academic_records = models.TextField(blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.student_id} - {self.list_name}"

    @property
    def list_name(self):
        given = f"{self.first_name} {self.middle_name}".strip()
        return f"{self.last_name}, {given}"

    @property
    def age(self):
        """Worked out from birth_date, so it is never stored or out of date."""
        today = date.today()
        had_birthday = (today.month, today.day) >= (self.birth_date.month, self.birth_date.day)
        return today.year - self.birth_date.year - (0 if had_birthday else 1)
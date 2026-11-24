
from datetime import date

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from enrollment.models import Enrollment, Program
from enrollment.services import (
    create_pending_enrollment,
    create_required_documents,
)

from .models import Student


User = get_user_model()

TW = (
    "w-full rounded-lg border border-slate-300 px-3 py-2 "
    "focus:outline-none focus:ring-2 focus:ring-blue-800"
)


class RegistrationForm(forms.ModelForm):

    # Account information
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password"}
        ),
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password"}
        ),
    )

    # Enrollment information
    program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        empty_label="Select a program",
    )

    year_level = forms.ChoiceField(
        choices=[
            ("", "Select year level")
        ] + list(Enrollment.YEAR_LEVEL_CHOICES)
    )

    academic_year = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={"placeholder": "2026-2027"}
        ),
    )

    semester = forms.ChoiceField(
        choices=[
            ("", "Select semester")
        ] + list(Enrollment.SEMESTER_CHOICES)
    )

    SECTIONS = [
        ("Account information", [
            "email",
            "password1",
            "password2",
        ]),
        ("Personal information", [
            "first_name",
            "middle_name",
            "last_name",
            "birth_date",
            "gender",
            "civil_status",
            "nationality",
            "contact_number",
            "address",
        ]),
        ("Family", [
            "father_name",
            "mother_name",
            "guardian_name",
            "guardian_contact",
            "guardian_occupation",
            "emergency_contact",
        ]),
        ("Previous education", [
            "previous_school",
            "school_address",
            "previous_year_level",
            "school_year",
            "academic_records",
        ]),
        ("Enrollment", [
            "program",
            "year_level",
            "academic_year",
            "semester",
        ]),
    ]

    class Meta:
        model = Student
        exclude = ("student_id", "user")

        widgets = {
            "birth_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "address": forms.Textarea(
                attrs={"rows": 2}
            ),
            "academic_records": forms.Textarea(
                attrs={"rows": 3}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", TW)

    @property
    def sections(self):
        """Return form fields grouped by registration sections."""

        used = set()
        result = []

        for title, names in self.SECTIONS:
            fields = [
                self[name]
                for name in names
                if name in self.fields
            ]

            used.update(names)

            if fields:
                result.append((title, fields))

        leftovers = [
            self[name]
            for name in self.fields
            if name not in used
        ]

        if leftovers:
            result.append(("Other", leftovers))

        return result

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        # Prevent duplicate student login accounts
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        if User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError(
                "This email is already being used as a username."
            )

        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    "Passwords do not match."
                )

            try:
                validate_password(password2)
            except ValidationError as error:
                raise forms.ValidationError(error.messages)

        return password2

    @staticmethod
    def _next_student_id():
        """Generate the next student ID based on the current year."""

        prefix = str(date.today().year)

        last = (
            Student.objects
            .filter(student_id__startswith=f"{prefix}-")
            .order_by("-student_id")
            .values_list("student_id", flat=True)
            .first()
        )

        number = int(last.split("-")[1]) + 1 if last else 1

        return f"{prefix}-{number:04d}"

    def register(self):
        """Create a user account, student profile, enrollment and documents."""

        data = self.cleaned_data

        with transaction.atomic():

            # 1. Create Django user account
            user = User.objects.create_user(
                username=data["email"],
                email=data["email"],
                password=data["password1"],
                is_staff=False,
                is_superuser=False,
            )

            # 2. Create student profile
            student = super().save(commit=False)

            student.student_id = self._next_student_id()
            student.user = user

            student.save()

            # 3. Create pending enrollment
            create_pending_enrollment(
                student,
                program=data["program"],
                year_level=data["year_level"],
                academic_year=data["academic_year"],
                semester=data["semester"],
            )

            # 4. Create required student documents
            create_required_documents(student)

        return student

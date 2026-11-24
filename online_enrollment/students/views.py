
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from config.permissions import staff_required
from enrollment.models import Enrollment, Program

from .forms import RegistrationForm
from .models import Student


@staff_required
def student_list(request):
    # Get search and filter values
    q = request.GET.get("q", "").strip()
    program = request.GET.get("program", "").strip()
    year_level = request.GET.get("year_level", "").strip()
    status = request.GET.get("status", "").strip()
    gender = request.GET.get("gender", "").strip()

    # Get all students and their enrollment records
    students_qs = Student.objects.prefetch_related(
        "enrollments__program"
    )

    # Search students by name or student ID
    for word in q.split():
        students_qs = students_qs.filter(
            Q(first_name__icontains=word)
            | Q(middle_name__icontains=word)
            | Q(last_name__icontains=word)
            | Q(student_id__icontains=word)
        )

    # Filter by gender
    if gender:
        students_qs = students_qs.filter(gender=gender)

    students = []

    # Count enrollment statuses
    counts = {
        "Enrolled": 0,
        "Pending": 0,
        "Dropped": 0,
    }

    for student in students_qs:
        # Get the latest enrollment
        enrollments = sorted(
            student.enrollments.all(),
            key=lambda enrollment: (
                enrollment.enrollment_date,
                enrollment.pk,
            ),
            reverse=True,
        )

        latest = enrollments[0] if enrollments else None
        student.latest_enrollment = latest

        # Apply enrollment filters
        if program and (
            latest is None or latest.program.code != program
        ):
            continue

        if year_level and (
            latest is None or str(latest.year_level) != year_level
        ):
            continue

        if status and (
            latest is None
            or latest.status.lower() != status.lower()
        ):
            continue

        students.append(student)

        # Count the latest enrollment status
        if latest:
            counts[latest.status] = counts.get(latest.status, 0) + 1

    context = {
        "page_title": "Student List",
        "students": students,
        "total_students": len(students),
        "all_students_count": Student.objects.count(),

        "enrolled_count": counts.get("Enrolled", 0),
        "pending_count": counts.get("Pending", 0),
        "dropped_count": counts.get("Dropped", 0),

        # Preserve selected filters
        "q": q,
        "selected_program": program,
        "selected_year_level": year_level,
        "selected_status": status,
        "selected_gender": gender,

        "has_filters": any([
            q,
            program,
            year_level,
            status,
            gender,
        ]),

        # Dropdown choices
        "programs": Program.objects.order_by("code"),
        "year_level_choices": Enrollment._meta.get_field(
            "year_level"
        ).choices,
        "status_choices": Enrollment._meta.get_field(
            "status"
        ).choices,
        "gender_choices": Student._meta.get_field(
            "gender"
        ).choices,
    }

    return render(
        request,
        "students/student_list.html",
        context,
    )


@login_required
def student_profile(request, pk):
    # Get the requested student
    student = get_object_or_404(Student, pk=pk)

    # Admin/staff can view all student profiles.
    # Students can only view their own profile.
    if not request.user.is_staff:
        if student.user_id != request.user.id:
            raise PermissionDenied

    # Get the latest enrollment
    latest = (
        student.enrollments
        .select_related("program")
        .order_by("-enrollment_date", "-pk")
        .first()
    )

    # Personal information
    student.full_name = " ".join(
        part
        for part in [
            student.first_name,
            student.middle_name,
            student.last_name,
        ]
        if part
    )

    # Enrollment information
    student.program = latest.program.code if latest else "—"
    student.year_level = latest.year_level if latest else "—"
    student.section = (
        latest.section or "—"
    ) if latest else "—"

    student.academic_year = (
        latest.academic_year if latest else "—"
    )

    student.semester = (
        latest.get_semester_display() if latest else "—"
    )

    student.enrollment_date = (
        latest.enrollment_date if latest else "—"
    )

    student.status = (
        latest.status.lower() if latest else "pending"
    )

    return render(
        request,
        "students/student_profile.html",
        {"student": student},
    )


def register(request):
    """Public student registration."""

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            student = form.register()

            request.session["registered_student_id"] = (
                student.student_id
            )

            return redirect("students:register_success")

    else:
        form = RegistrationForm()

    context = {
        "form": form,
        "page_title": "Student Registration",
    }

    return render(
        request,
        "students/register.html",
        context,
    )


def register_success(request):
    """Display successful student registration."""

    student_id = request.session.get(
        "registered_student_id"
    )

    if not student_id:
        return redirect("students:register")

    return render(
        request,
        "students/register_success.html",
        {
            "student_id": student_id,
            "page_title": "Registration received",
        },
    )

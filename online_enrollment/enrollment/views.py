
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from students.models import Student

from .forms import EnrollmentForm
from .models import Enrollment
from .services import create_pending_enrollment


def is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def enrollment_list(request):
    """Admin: view and manage all enrollment records."""

    enrollments = Enrollment.objects.select_related(
        "student",
        "program",
    )

    status = request.GET.get("status", "").strip()
    q = request.GET.get("q", "").strip()

    if status:
        enrollments = enrollments.filter(status=status)

    for word in q.split():
        enrollments = enrollments.filter(
            Q(student__first_name__icontains=word)
            | Q(student__middle_name__icontains=word)
            | Q(student__last_name__icontains=word)
            | Q(student__student_id__icontains=word)
        )

    context = {
        "page_title": "Enrollment",
        "enrollments": enrollments,
        "selected_status": status,
        "q": q,
    }

    return render(
        request,
        "enrollment/enrollment_list.html",
        context,
    )


@login_required
def enroll(request, student_id):
    """Allow a student to enroll themselves or an admin to enroll a student."""

    student = get_object_or_404(Student, pk=student_id)

    if not request.user.is_staff:
        if student.user_id != request.user.id:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied

    form = EnrollmentForm(
        request.POST or None,
        student=student,
    )

    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data

        create_pending_enrollment(
            student,
            program=data["program"],
            year_level=data["year_level"],
            academic_year=data["academic_year"],
            semester=data["semester"],
        )

        messages.success(
            request,
            "Enrollment submitted. Waiting for approval.",
        )

        return redirect(
            "students:profile",
            pk=student.pk,
        )

    context = {
        "form": form,
        "student": student,
        "page_title": "Enroll Student",
    }

    return render(
        request,
        "enrollment/enroll_form.html",
        context,
    )


@login_required
@user_passes_test(is_admin)
@require_POST
def set_status(request, pk, status):
    """Admin: update an enrollment status."""

    enrollment = get_object_or_404(
        Enrollment,
        pk=pk,
    )

    valid_statuses = {
        "Pending",
        "Enrolled",
        "Dropped",
    }

    if status not in valid_statuses:
        messages.error(request, "Invalid enrollment status.")
        return redirect("enrollment:list")

    enrollment.status = status
    enrollment.save(update_fields=["status"])

    messages.success(
        request,
        f"Enrollment marked as {status}.",
    )

    return redirect(
        request.META.get("HTTP_REFERER")
        or "enrollment:list"
    )

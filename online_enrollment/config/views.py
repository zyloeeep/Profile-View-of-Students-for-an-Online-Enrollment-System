from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect
from django.views.decorators.http import require_POST


@require_POST
def demo_admin_login(request):
    """One-click admin login for the class demo (DEBUG only)."""
    if not settings.DEBUG:
        raise Http404

    admin = get_user_model().objects.filter(is_superuser=True).first()

    if admin is None:
        messages.error(request, "No admin account found.")
        return redirect("login")

    login(request, admin, backend="django.contrib.auth.backends.ModelBackend")
    return redirect("role_redirect")


@login_required
def role_redirect(request):

    # Admin account
    if request.user.is_staff:
        return redirect("enrollment:list")

    # Student account
    student = getattr(
        request.user,
        "student_profile",
        None,
    )

    if student:
        return redirect(
            "students:profile",
            pk=student.pk,
        )

    # Account without a student profile
    logout(request)

    messages.error(
        request,
        "This account isn't linked to a student record.",
    )

    return redirect("login")
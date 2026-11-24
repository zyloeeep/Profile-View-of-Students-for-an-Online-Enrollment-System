
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


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

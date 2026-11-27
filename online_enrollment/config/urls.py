from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views as config_views
from .forms import EmailLoginForm


urlpatterns = [
    path(
        "",
        config_views.role_redirect,
        name="role_redirect",
    ),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="login.html",
            authentication_form=EmailLoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path("admin/", admin.site.urls),

    path("students/", include("students.urls")),

    path("enrollment/", include("enrollment.urls")),
]

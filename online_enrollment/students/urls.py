from django.urls import path
from . import views

app_name = "students"

urlpatterns = [
    path("", views.student_list, name="list"),
    path("register/", views.register, name="register"),
    path("register/success/", views.register_success, name="register_success"),
    path("<int:pk>/", views.student_profile, name="profile"),
]
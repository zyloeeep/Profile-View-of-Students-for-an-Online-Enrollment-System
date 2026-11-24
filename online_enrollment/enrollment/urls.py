from django.urls import path
from . import views

app_name = "enrollment"

urlpatterns = [
    path("", views.enrollment_list, name="list"),
    path("student/<int:student_id>/enroll/", views.enroll, name="enroll"),
    path("<int:pk>/status/<str:status>/", views.set_status, name="set_status"),
]
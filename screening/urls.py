from django.urls import path
from . import views

app_name = "screening"

urlpatterns = [
    path("questionnaire/", views.questionnaire_create, name="questionnaire"),

    path(
        "health-record/<int:questionnaire_id>/",
        views.health_record_create,
        name="health_record",
    ),

    path(
        "result/<int:prediction_id>/",
        views.result_detail,
        name="result_detail",
    ),

    path(
        "doctor/dashboard/",
        views.doctor_dashboard,
        name="doctor_dashboard",
    ),

    path(
        "doctor/decision/<int:prediction_id>/",
        views.doctor_decision,
        name="doctor_decision",
    ),
]
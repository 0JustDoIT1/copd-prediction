from django.urls import path
from . import views

app_name = "screening"

urlpatterns = [
    path("", views.screening_home, name="home"),
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
    
    path(
    "results/",
    views.result_list,
    name="result_list",
    ),

    path(
    "ocr/<int:questionnaire_id>/",
    views.ocr_upload,
    name="ocr_upload",
    ),

    # What-if 시뮬레이션 - accounts.views.patient_dashboard_view가
    # reverse('screening:predict_whatif')로 이 경로를 가져다 쓴다.
    path(
    "predict/what-if/",
    views.predict_whatif,
    name="predict_whatif",
    ),
]
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard", views.patient_dashboard, name="patient_dashboard"),
    path("doctor/dashboard", views.doctor_dashboard, name="doctor_dashboard"),

    path("signup", views.signup, name="signup"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
]
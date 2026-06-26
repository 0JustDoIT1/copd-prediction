from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.root_view, name='root'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('signup/', views.signup_role_select_view, name='signup'),
    path('signup/patient/', views.signup_patient_view, name='signup_patient'),
    path('signup/doctor/', views.signup_doctor_view, name='signup_doctor'),

    path('dashboard/patient/', views.patient_dashboard_view, name='patient_dashboard'),
    path('profile/', views.profile_view, name='profile'),
]
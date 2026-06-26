from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_request, name='appointment_request'),
    path('confirm/', views.appointment_confirm, name='appointment_confirm'),
    path('done/', views.appointment_done, name='appointment_done'),
]
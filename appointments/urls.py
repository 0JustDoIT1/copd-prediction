from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_request, name='appointment_request'),
    path('confirm/', views.appointment_confirm, name='appointment_confirm'),
    path('done/', views.appointment_done, name='appointment_done'),
    path('list/', views.appointment_list, name='appointment_list'),  
    path('my/', views.my_appointments, name='my_appointments'),
    path('cancel/<int:pk>/', views.cancel_appointment, name='cancel_appointment'),
]
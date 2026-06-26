from django.urls import path

from . import views

app_name = 'content'

urlpatterns = [
    path('health-tips/', views.health_tip_list_view, name='health_tips'),
    path('breathing-guides/', views.breathing_exercise_list_view, name='breathing_guides'),
    path('faq/', views.faq_list_view, name='faq'),
]
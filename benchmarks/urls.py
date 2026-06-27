from django.urls import path
from . import views

app_name = 'benchmarks'

urlpatterns = [
    path('', views.risk_factors_view, name='risk_factors'),
    path('age-compare/', views.age_compare_view, name='age_compare'),
    path('timeline/', views.timeline_view, name='timeline'),
]
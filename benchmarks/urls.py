from django.urls import path
from . import views

app_name = 'benchmarks'

urlpatterns = [
    path('age-compare/', views.age_compare_view, name='age_compare'),
    path('timeline/', views.timeline_view, name='timeline'),
]
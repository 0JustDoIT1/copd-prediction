from django.urls import path

from . import views

app_name = "daily_care"

urlpatterns = [
    # 추세 그래프 대시보드 (홈)
    path("", views.DashboardView.as_view(), name="dashboard"),
    # 기록 입력
    path("checkin/", views.CheckinView.as_view(), name="checkin"),
    # 히스토리 목록
    path("history/", views.HistoryView.as_view(), name="history"),

    path("calendar/events/", views.calendar_events_api, name="calendar_events"),
    path('history/<int:pk>/edit/', views.LogUpdateView.as_view(), name='log_edit'),

]
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
]
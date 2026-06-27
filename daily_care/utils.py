# daily_care/utils.py

from django.utils import timezone
from .models import DailyLog

def has_checked_in_today(user) -> bool:
    """오늘 daily_log를 기록했는지 여부를 반환"""
    today = timezone.localdate()
    return DailyLog.objects.filter(
        user=user,
        log_date=today
    ).exists()
# daily_care/admin.py
from django.contrib import admin
from .models import DailyLog


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "log_date", "breath_score", "smoked_today", "cigarette_count")
    list_filter = ("smoked_today", "log_date")
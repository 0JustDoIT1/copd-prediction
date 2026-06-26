from django.contrib import admin
from .models import DailyLog

@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = (
        "log_date",
        "user",
        "smoking_count",
        "dyspnea_grade",
        "spo2",
        "has_cough",
        "has_sputum",
        "exercised",
        "created_at",
    )
    list_filter = ("log_date", "dyspnea_grade", "exercised")
    search_fields = ("user__username", "memo")
    date_hierarchy = "log_date"
    ordering = ("-log_date",)
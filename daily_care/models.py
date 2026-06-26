from datetime import date
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

DYSPNEA_CHOICES = [(i, str(i)) for i in range(5)]

class DailyLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="daily_logs",
        verbose_name="사용자",
    )
    log_date = models.DateField("기록 날짜", default=date.today)

    smoking_count = models.PositiveSmallIntegerField("흡연량(개비)", default=0)
    dyspnea_grade = models.IntegerField("호흡 곤란 등급", choices=DYSPNEA_CHOICES, default=0)
    spo2 = models.DecimalField("산소포화도", max_digits=4, decimal_places=1, null=True, blank=True)
    has_cough = models.BooleanField("기침 여부", default=False)
    has_sputum = models.BooleanField("가래 여부", default=False)
    exercised = models.BooleanField("운동 여부", default=False)
    memo = models.TextField("메모", blank=True, default="")

    created_at = models.DateTimeField("작성일시", auto_now_add=True)

    class Meta:
        verbose_name = "일상 케어 로그"
        verbose_name_plural = "일상 케어 로그 목록"
        ordering = ["-log_date"]
        unique_together = ("user", "log_date")

    def __str__(self):
        return f"{self.user} │ {self.log_date} │ 흡연 {self.smoking_count}개비"
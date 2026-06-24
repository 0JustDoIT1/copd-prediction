from django.db import models
from accounts.models import PatientProfile


class DailyLog(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='daily_logs')
    log_date = models.DateField()
    breath_score = models.IntegerField()
    smoked_today = models.BooleanField(default=False)
    cigarette_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('patient', 'log_date')
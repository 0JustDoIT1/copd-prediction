from django.db import models
from accounts.models import PatientProfile
from screening.models import ClinicalDecision


class AppointmentRequest(models.Model):
    STATUS_CHOICES = [('requested', '요청됨'), ('confirmed', '확정'), ('cancelled', '취소')]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    decision = models.ForeignKey(ClinicalDecision, on_delete=models.CASCADE, related_name='appointments')
    preferred_datetime = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='requested')
    requested_at = models.DateTimeField(auto_now_add=True)
from django.db import models
from accounts.models import PatientProfile
from screening.models import ClinicalDecision


class AppointmentRequest(models.Model):
    STATUS_CHOICES = [
        ('confirmed', '확정'),
        ('cancelled', '취소'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)    
    decision = models.ForeignKey(ClinicalDecision, on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    slot_datetime = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='confirmed')
    note = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('slot_datetime',),)
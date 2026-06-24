from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('patient', '환자'),
        ('doctor', '의사'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)


class PatientProfile(models.Model):
    SEX_CHOICES = [('M', '남성'), ('F', '여성')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    birth_date = models.DateField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)

    def __str__(self):
        return f"{self.user.username} (Patient)"


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    license_no = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user.username} (Doctor)"
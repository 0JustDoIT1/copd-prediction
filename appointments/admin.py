# appointments/admin.py
from django.contrib import admin
from .models import AppointmentRequest


@admin.register(AppointmentRequest)
class AppointmentRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "decision", "preferred_datetime", "status", "requested_at")
    list_filter = ("status",)
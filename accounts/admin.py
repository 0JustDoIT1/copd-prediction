# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PatientProfile, DoctorProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """AUTH_USER_MODEL이라 기본 UserAdmin을 상속, role 필드 노출"""
    list_display = ("username", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username",)
    fieldsets = UserAdmin.fieldsets + (
        ("역할 정보", {"fields": ("role",)}),
    )


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "birth_date", "sex")
    list_filter = ("sex",)
    search_fields = ("user__username",)


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "license_no")
    search_fields = ("user__username", "license_no")
# benchmarks/admin.py
from django.contrib import admin
from .models import Benchmark


@admin.register(Benchmark)
class BenchmarkAdmin(admin.ModelAdmin):
    list_display = ("id", "age_group", "sex", "variable_name", "mean_value")
    list_filter = ("age_group", "sex")
    search_fields = ("variable_name",)
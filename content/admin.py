from django.contrib import admin

from .models import FAQ, BreathingExercise, HealthTip


@admin.register(HealthTip)
class HealthTipAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    search_fields = ('title', 'body')


@admin.register(BreathingExercise)
class BreathingExerciseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    search_fields = ('title', 'steps')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'order')
    list_editable = ('order',)
    search_fields = ('question', 'answer')
    ordering = ('order', 'id')
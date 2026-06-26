from django.shortcuts import render

from .models import FAQ, BreathingExercise, HealthTip


def health_tip_list_view(request):
    tips = HealthTip.objects.all()
    return render(request, 'content/health_tip_list.html', {
        'tips': tips,
        'active_menu': 'health_tips',
    })


def breathing_exercise_list_view(request):
    exercises = BreathingExercise.objects.all()
    return render(request, 'content/breathing_exercise_list.html', {
        'exercises': exercises,
        'active_menu': 'breathing_guides',
    })


def faq_list_view(request):
    faqs = FAQ.objects.all()
    return render(request, 'content/faq_list.html', {
        'faqs': faqs,
        'active_menu': 'faq',
    })
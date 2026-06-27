from django.shortcuts import render

from .models import FAQ, BreathingExercise, HealthTip


def health_tip_list_view(request):
    tips = HealthTip.objects.all().order_by('category', 'id')

    grouped = {'disease': [], 'lifestyle': [], 'factor': []}
    for tip in tips:
        grouped[tip.category].append(tip)

    grouped_tips = [
        {'key': 'disease', 'label': '질환/검사 이해', 'icon': 'bi-clipboard2-pulse', 'tips': grouped['disease']},
        {'key': 'lifestyle', 'label': '생활관리 팁', 'icon': 'bi-heart-pulse', 'tips': grouped['lifestyle']},
        {'key': 'factor', 'label': '관련 요인 살펴보기', 'icon': 'bi-graph-up', 'tips': grouped['factor']},
    ]

    return render(request, 'content/health_tip_list.html', {
        'grouped_tips': grouped_tips,
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
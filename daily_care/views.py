import json
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, TemplateView

from .forms import DailyLogForm
from .models import DailyLog


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'daily_care/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.localdate()

        # 오늘 체크인 여부
        today_log = DailyLog.objects.filter(user=user, log_date=today).first()
        context['checked_in_today'] = today_log is not None
        context['today_log'] = today_log

        # 최근 30일 데이터
        start = today - timedelta(days=29)
        logs = DailyLog.objects.filter(
            user=user, log_date__range=(start, today)
        ).order_by('log_date')

        # 차트 데이터
        context['chart_labels']  = json.dumps([str(l.log_date) for l in logs])
        context['chart_smoking'] = json.dumps([l.smoking_count for l in logs])
        context['chart_grade']   = json.dumps([l.dyspnea_grade for l in logs])

        # 주간 달성률 도트
        weekly = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            weekly.append({
                'date': d,
                'checked': logs.filter(log_date=d).exists(),
                'day': '일월화수목금토'[d.weekday() % 7],
            })
        checked_count = sum(1 for w in weekly if w['checked'])
        context['weekly'] = weekly
        context['weekly_rate'] = round(checked_count / 7 * 100)

        return context


class CheckinView(LoginRequiredMixin, CreateView):
    model = DailyLog
    form_class = DailyLogForm
    template_name = 'daily_care/checkin.html'
    success_url = reverse_lazy('daily_care:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        context['checked_in_today'] = DailyLog.objects.filter(
            user=self.request.user, log_date=today
        ).exists()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.log_date = timezone.localdate()

        already_exists = DailyLog.objects.filter(
            user=self.request.user, log_date=form.instance.log_date
        ).exists()
        if already_exists:
            form.add_error(None, "오늘은 이미 일상 체크인을 완료하셨습니다. 수정은 히스토리 메뉴를 이용해 주세요.")
            return self.form_invalid(form)

        return super().form_valid(form)


class HistoryView(LoginRequiredMixin, ListView):
    model = DailyLog
    template_name = 'daily_care/history.html'
    context_object_name = 'logs'

    def get_queryset(self):
        queryset = DailyLog.objects.filter(user=self.request.user)
        start_date = self.request.GET.get('start')
        end_date = self.request.GET.get('end')
        if start_date and end_date:
            queryset = queryset.filter(log_date__range=[start_date, end_date])
        return queryset.order_by('log_date')  # 차트용 오래된순 정렬

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()

        context['checked_in_today'] = DailyLog.objects.filter(
            user=self.request.user, log_date=today
        ).exists()

        # 요약 통계
        logs = context['logs']
        total_days = logs.count()
        context['avg_smoking'] = round(
            logs.aggregate(Avg('smoking_count'))['smoking_count__avg'] or 0, 1
        )
        context['avg_grade'] = round(
            logs.aggregate(Avg('dyspnea_grade'))['dyspnea_grade__avg'] or 0, 1
        )
        context['checkin_rate'] = round(total_days / 30 * 100) if total_days else 0

        return context
import json
from datetime import timedelta
from .utils import has_checked_in_today
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils import timezone

from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from .forms import DailyLogForm
from .models import DailyLog


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'daily_care/daily_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.localdate()

        today_log = DailyLog.objects.filter(user=user, log_date=today).first()
        context['checked_in_today'] = has_checked_in_today(user)
        context['today_log'] = today_log

        start = today - timedelta(days=29)
        logs = list(
            DailyLog.objects.filter(
                user=user, log_date__range=(start, today)
            ).order_by('log_date')
        )

        context['chart_labels']  = json.dumps([str(l.log_date) for l in logs])
        context['chart_smoking'] = json.dumps([l.smoking_count for l in logs])
        context['chart_grade']   = json.dumps([l.dyspnea_grade for l in logs])

        logged_dates = {l.log_date for l in logs}
        weekly = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            weekly.append({
                'date': d,
                'checked': d in logged_dates,
                'day': '월화수목금토일'[d.weekday()],
            })
        checked_count = sum(1 for w in weekly if w['checked'])
        context['weekly'] = weekly
        context['weekly_rate'] = round(checked_count / 7 * 100)

               # ── 월간(이번 달 1일 ~ 오늘) 체크인 달성률 ──
        month_start = today.replace(day=1)
        days_so_far = (today - month_start).days + 1        # 이번 달 1일부터 오늘까지 지난 일수
        month_logged = DailyLog.objects.filter(
            user=user, log_date__range=(month_start, today)
        ).values_list('log_date', flat=True).distinct().count()
        monthly_rate = round(month_logged / days_so_far * 100) if days_so_far else 0
        context['monthly_rate'] = monthly_rate
                # 원형 게이지 채움 계산 (둘레 2πr = 2 × 3.1416 × 40 ≈ 251.2)
        context['monthly_dashoffset'] = round(251.2 * (1 - monthly_rate / 100), 1)


        return context



class CheckinView(LoginRequiredMixin, CreateView):
    model = DailyLog
    form_class = DailyLogForm
    template_name = 'daily_care/daily_checkin.html'
    success_url = reverse_lazy('daily_care:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['checked_in_today'] = has_checked_in_today(self.request.user)
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.log_date = timezone.localdate()

        if DailyLog.objects.filter(
            user=self.request.user, log_date=form.instance.log_date
        ).exists():
            form.add_error(
                None,
                "오늘은 이미 일상 체크인을 완료하셨습니다. 수정은 히스토리 메뉴를 이용해 주세요.",
            )
            return self.form_invalid(form)

        try:
            return super().form_valid(form)
        except IntegrityError:
            form.add_error(None, "오늘은 이미 일상 체크인을 완료하셨습니다.")
            return self.form_invalid(form)


class HistoryView(LoginRequiredMixin, ListView):
    model = DailyLog
    template_name = 'daily_care/daily_history.html'
    context_object_name = 'logs'

    def get_queryset(self):
        queryset = DailyLog.objects.filter(user=self.request.user)
        start_date = self.request.GET.get('start')
        end_date = self.request.GET.get('end')
        if start_date and end_date:
            queryset = queryset.filter(log_date__range=[start_date, end_date])
        return queryset.order_by('log_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['checked_in_today'] = has_checked_in_today(self.request.user)

        logs = list(context['logs'])
        total_days = len(logs)

        if total_days:
            context['avg_smoking'] = round(
                sum(l.smoking_count for l in logs) / total_days, 1
            )
            context['avg_grade'] = round(
                sum(l.dyspnea_grade for l in logs) / total_days, 1
            )
        else:
            context['avg_smoking'] = 0
            context['avg_grade'] = 0

        start_date = self.request.GET.get('start')
        end_date = self.request.GET.get('end')
        period_days = 30
        if start_date and end_date:
            try:
                s = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                e = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
                period_days = (e - s).days + 1
            except (ValueError, TypeError):
                period_days = 30
        context['checkin_rate'] = round(total_days / period_days * 100) if period_days else 0

        return context


# ── 클래스 밖 ──
@login_required
def calendar_events_api(request):
    logs = DailyLog.objects.filter(user=request.user).values(
        'log_date', 'smoking_count', 'dyspnea_grade',
        'spo2', 'has_cough', 'has_sputum', 'exercised', 'memo'
    )
    events = []
    for log in logs:
        grade = log['dyspnea_grade']
        if grade >= 3:
            color = '#EF4444'
        elif grade >= 2:
            color = '#F59E0B'
        else:
            color = '#0D9488'

        events.append({
            "title": f"🚬{log['smoking_count']} mMRC{grade}",
            "start": str(log['log_date']),
            "color": color,
            "extendedProps": {
                "smoking_count": log['smoking_count'],
                "dyspnea_grade": grade,
                "spo2": log['spo2'],
                "has_cough": log['has_cough'],
                "has_sputum": log['has_sputum'],
                "exercised": log['exercised'],
                "memo": log['memo'] or "",
            },
        })
    return JsonResponse(events, safe=False)

class LogUpdateView(LoginRequiredMixin, UpdateView):
    model = DailyLog
    form_class = DailyLogForm
    template_name = 'daily_care/daily_log_edit.html'
    success_url = reverse_lazy('daily_care:history')

    def get_queryset(self):
        # 본인 기록만 수정 가능 (URL의 pk를 바꿔 남의 기록 접근하는 것 차단)
        return DailyLog.objects.filter(user=self.request.user)

    def form_valid(self, form):
        # log_date는 수정 시 변경하지 않음 — DB의 기존 날짜를 그대로 유지
        # (unique_together 충돌 방지). 폼에 log_date가 있어도 원본 값으로 되돌림.
        form.instance.log_date = self.get_object().log_date
        return super().form_valid(form)

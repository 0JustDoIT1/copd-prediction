import json
from datetime import timedelta
from .utils import has_checked_in_today
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError

from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, TemplateView

from .forms import DailyLogForm
from .models import DailyLog


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'daily_care/daily_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.localdate()

        # 오늘 체크인 여부
        today_log = DailyLog.objects.filter(user=user, log_date=today).first()
        context['checked_in_today'] = has_checked_in_today(user)
        context['today_log'] = today_log

        # 최근 30일 데이터 (한 번만 조회해서 재사용)
        start = today - timedelta(days=29)
        logs = list(
            DailyLog.objects.filter(
                user=user, log_date__range=(start, today)
            ).order_by('log_date')
        )

        # 차트 데이터
        context['chart_labels']  = json.dumps([str(l.log_date) for l in logs])
        context['chart_smoking'] = json.dumps([l.smoking_count for l in logs])
        context['chart_grade']   = json.dumps([l.dyspnea_grade for l in logs])

        # 주간 달성률 도트 (이미 가져온 30일 데이터 재사용 → 추가 쿼리 없음)
        logged_dates = {l.log_date for l in logs}
        weekly = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            weekly.append({
                'date': d,
                'checked': d in logged_dates,
                'day': '월화수목금토일'[d.weekday()],  # weekday(): 월=0 … 일=6
            })
        checked_count = sum(1 for w in weekly if w['checked'])
        context['weekly'] = weekly
        context['weekly_rate'] = round(checked_count / 7 * 100)

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

        # 1차: 일반 중복 체크인 차단
        if DailyLog.objects.filter(
            user=self.request.user, log_date=form.instance.log_date
        ).exists():
            form.add_error(
                None,
                "오늘은 이미 일상 체크인을 완료하셨습니다. 수정은 히스토리 메뉴를 이용해 주세요.",
            )
            return self.form_invalid(form)

        # 2차: 동시 제출(레이스 컨디션) 시 DB unique 제약 방어
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
        return queryset.order_by('log_date')  # 템플릿에서 reversed로 뒤집어 사용

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['checked_in_today'] = has_checked_in_today(self.request.user)

        logs = list(context['logs'])  # 한 번만 평가
        total_days = len(logs)

        # ── 통계 카드용 요약 (차트는 템플릿이 직접 그림) ──
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

        # 달성률: 조회 기간이 지정되면 그 일수 기준, 아니면 30일 기준
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

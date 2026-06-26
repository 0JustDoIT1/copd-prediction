from django.db import models


class HealthTip(models.Model):
    """오늘의 COPD 상식. 대시보드에서는 날짜 기준으로 하나씩 로테이션해서 보여주고,
    전체 목록 페이지에서는 등록된 전부를 보여준다."""

    title = models.CharField('제목', max_length=100)
    body = models.TextField('본문')
    source = models.CharField(
        '출처/근거', max_length=200, blank=True,
        help_text='참고문헌이나 근거를 짧게 표기 (선택)',
    )
    created_at = models.DateTimeField('등록일', auto_now_add=True)

    class Meta:
        verbose_name = 'COPD 상식'
        verbose_name_plural = 'COPD 상식 목록'
        ordering = ['id']

    def __str__(self):
        return self.title


class BreathingExercise(models.Model):
    """호흡 운동 가이드. 대시보드에서는 날짜 기준으로 하나씩 로테이션."""

    title = models.CharField('제목', max_length=100)
    steps = models.TextField('방법 설명')
    created_at = models.DateTimeField('등록일', auto_now_add=True)

    class Meta:
        verbose_name = '호흡 운동 가이드'
        verbose_name_plural = '호흡 운동 가이드 목록'
        ordering = ['id']

    def __str__(self):
        return self.title


class FAQ(models.Model):
    """자주 묻는 질문. order로 노출 순서를 직접 관리한다."""

    question = models.CharField('질문', max_length=200)
    answer = models.TextField('답변')
    order = models.PositiveIntegerField('노출 순서', default=0)
    created_at = models.DateTimeField('등록일', auto_now_add=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQ 목록'
        ordering = ['order', 'id']

    def __str__(self):
        return self.question
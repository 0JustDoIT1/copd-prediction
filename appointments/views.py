import re

from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import datetime
from .models import AppointmentRequest
from accounts.models import PatientProfile
from django.db import transaction, IntegrityError
from django.utils import timezone as tz
from datetime import timedelta
from django.db import models

SLOT_TIMES_AM = [
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
]

SLOT_TIMES_PM = [
    "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
    "16:00", "16:30", "17:00", "17:30",
]

SLOT_TIMES_SAT = [
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
]


def _strip_day_of_week(date_str):
    """
    '2026년 6월 30일 (화)' 형태에서 요일 표시 ' (화)'를 제거해
    '2026년 6월 30일'만 남긴다.

    appointment_confirm()에서 화면 표시용으로 날짜 뒤에 요일을 붙인
    selected_date_with_day를 그대로 hidden input에 흘려보내면서,
    appointment_done()의 strptime 포맷("%Y년 %m월 %d일")과 안 맞아
    ValueError가 나고, 그게 bare except에 조용히 삼켜져 "예약은 성공한
    것처럼 보이는데 실제로는 저장이 안 되는" 버그로 이어졌었다.
    요일이 없는 입력(예: 이전 버전 호환)도 그대로 통과하도록
    정규식이 매치 안 되면 원본을 그대로 반환한다.
    """
    return re.sub(r"\s*\([일월화수목금토]\)\s*$", "", date_str).strip()


def appointment_request(request):
    if request.GET.get('back'):
        saved_date = request.session.get('selected_date', '')
        saved_time = request.session.get('selected_time', '')
    else:
        saved_date = ''
        saved_time = ''
        request.session.pop('selected_date', None)
        request.session.pop('selected_time', None)
    
    booked_slots = list(AppointmentRequest.objects.filter(status='confirmed').values_list('slot_datetime', flat=True))
    booked_times = [f"{tz.localtime(slot).year}년 {tz.localtime(slot).month}월 {tz.localtime(slot).day}일|{tz.localtime(slot).strftime('%H:%M')}" for slot in booked_slots]

    return render(request, 'appointments/appointment_request.html', {
        'slot_times_am': SLOT_TIMES_AM,
        'slot_times_pm': SLOT_TIMES_PM,
        'slot_times_sat': SLOT_TIMES_SAT,
        'saved_date': saved_date,
        'saved_time': saved_time,
        'booked_times': booked_times,
        'active_group': 'appointments',
        'active_menu': 'appointment_request',
    })


def appointment_confirm(request):
    # appointment_request.html의 selectDay()가 slot-label에 이미 요일을 붙여서
    # ("2026년 6월 30일 (화)") 표시하고, goToConfirm()이 그 텍스트를 그대로
    # date 쿼리파라미터로 보낸다. 즉 여기 도착하는 시점부터 이미 요일이 붙어
    # 있으므로, 가장 먼저 _strip_day_of_week()로 요일을 떼어내 "요일 없는
    # 원본"을 확정해야 한다. 이걸 안 하면 selected_date_raw도 요일이 포함된
    # 채로 넘어가서, appointment_done()의 파싱이 다시 깨진다.
    selected_date_raw = _strip_day_of_week(request.GET.get('date', ''))
    selected_time = request.GET.get('time', '')
    request.session['selected_date'] = selected_date_raw
    request.session['selected_time'] = selected_time
    
    DAYS_KO = ['월', '화', '수', '목', '금', '토', '일']
    from datetime import datetime as dt
    if selected_date_raw:
        try:
            parsed = dt.strptime(selected_date_raw, "%Y년 %m월 %d일")
            day_of_week = DAYS_KO[parsed.weekday()]
            selected_date_with_day = f"{selected_date_raw} ({day_of_week})"
        except ValueError:
            # 요일을 뗀 뒤에도 형식이 안 맞으면(예상치 못한 입력), 화면 표시는
            # 원본을 그대로 보여주되 저장용 raw 값은 그대로 유지한다.
            selected_date_with_day = selected_date_raw
    else:
        selected_date_with_day = selected_date_raw
        
        
    try:
        # 주의: 'patientprofile'이 맞는 속성명 (accounts.PatientProfile의 OneToOneField 역참조).
        # 'patient_profile'(언더스코어 포함)은 존재하지 않는 속성이라 항상 예외가 나서
        # patient가 None으로만 저장되던 버그가 있었음 - 수정됨.
        patient = request.user.patientprofile
    except PatientProfile.DoesNotExist:
        patient = None
        
    hour = int(selected_time.split(':')[0]) if selected_time else 0
    ampm = '오전' if hour < 12 else '오후'
    
    return render(request, 'appointments/appointment_confirm.html', {
        # 화면에는 요일이 붙은 버전을 보여주되, 폼 hidden input의 실제
        # 제출값(date)은 appointment_confirm.html에서 selected_date_raw(요일
        # 없는 원본)를 쓴다.
        'selected_date': selected_date_with_day,
        'selected_date_raw': selected_date_raw,
        'selected_time': selected_time,
        'patient': patient,
        'ampm': ampm,
        'active_group': 'appointments',
        'active_menu': 'appointment_request',
    })


def appointment_done(request):
    if request.method == 'POST':
        date_str = request.POST.get('date', '')
        time_str = request.POST.get('time', '')
        note = request.POST.get('note', '')

        # 요일이 붙어 들어와도(예: '2026년 6월 30일 (화)') 파싱 가능하게
        # 정리한다. appointment_confirm.html의 hidden input이 요일 포함
        # 버전을 보내고 있어도 여기서 안전하게 방어된다.
        date_str_clean = _strip_day_of_week(date_str)
        
        try:
            patient = request.user.patientprofile
        except PatientProfile.DoesNotExist:
            patient = None
        
        try:
            slot_datetime = datetime.strptime(f"{date_str_clean} {time_str}", "%Y년 %m월 %d일 %H:%M")
            slot_datetime = timezone.make_aware(slot_datetime)
            
            with transaction.atomic():
                if AppointmentRequest.objects.select_for_update().filter(
                    slot_datetime=slot_datetime,
                    status = 'confirmed'
                ).exists():
                    return render(request, 'appointments/appointment_confirm.html', {
                        'selected_date': date_str,
                        'selected_date_raw': date_str_clean,
                        'selected_time': time_str,
                        'patient': patient,
                        'error': '이미 예약된 시간입니다. 다른 시간을 선택해주세요.',
                        'active_group': 'appointments',
                        'active_menu': 'appointment_request',
                    })
                
                AppointmentRequest.objects.create(
                    patient=patient,
                    slot_datetime=slot_datetime,
                    note=note,
                    status='confirmed',
                )
        except IntegrityError:
            return render(request, 'appointments/appointment_confirm.html', {
                'selected_date': date_str,
                'selected_date_raw': date_str_clean,
                'selected_time': time_str,
                'patient': patient,
                'error': '이미 예약된 시간입니다. 다른 시간을 선택해주세요.',
                'active_group': 'appointments',
                'active_menu': 'appointment_request',
            })
        except ValueError as e:
            # 날짜/시간 형식 자체가 깨진 경우 - 조용히 넘기지 않고 사용자에게
            # 바로 알려서, "예약된 것처럼 보이는데 실제로는 저장 안 됨" 같은
            # 상황이 다시는 생기지 않게 한다.
            print(f"예약 날짜/시간 파싱 오류: {e}")
            return render(request, 'appointments/appointment_confirm.html', {
                'selected_date': date_str,
                'selected_date_raw': date_str_clean,
                'selected_time': time_str,
                'patient': patient,
                'error': '예약 날짜 또는 시간 형식이 올바르지 않습니다. 다시 시도해주세요.',
                'active_group': 'appointments',
                'active_menu': 'appointment_request',
            })
        except Exception as e:
            import traceback
            print(f"예약 저장 오류: {type(e).__name__}: {e}")
            traceback.print_exc()
            return render(request, 'appointments/appointment_confirm.html', {
                'selected_date': date_str,
                'selected_date_raw': date_str_clean,
                'selected_time': time_str,
                'patient': patient,
                'error': '예약 처리 중 오류가 발생했습니다. 다시 시도해주세요.',
                'active_group': 'appointments',
                'active_menu': 'appointment_request',
            })
        
        request.session.pop('selected_date', None)
        request.session.pop('selected_time', None)
        request.session['appointment_date'] = date_str_clean
        request.session['appointment_time'] = time_str
        return redirect('appointments:appointment_done')
    
    date_str = request.session.get('appointment_date', '')
    time_str = request.session.get('appointment_time', '')
    hour = int(time_str.split(':')[0]) if time_str else 0
    ampm = '오전' if hour < 12 else '오후'
    
    DAYS_KO = ['월', '화', '수', '목', '금', '토', '일']
    if date_str:
        try:
            from datetime import datetime as dt
            parsed = dt.strptime(date_str, "%Y년 %m월 %d일")
            day_of_week = DAYS_KO[parsed.weekday()]
            date_str = f"{date_str} ({day_of_week})"
        except:
            pass
        
    return render(request, 'appointments/appointment_done.html', {
        'date': date_str,
        'time': time_str,
        'ampm': ampm,
        'active_group': 'appointments',
        'active_menu': 'appointment_request',
    })


def appointment_list(request):
    appointments = AppointmentRequest.objects.select_related(
        'patient__user'
    ).order_by('slot_datetime')
    
    return render(request, 'appointments/appointment_list.html', {
        'appointments': appointments,
        'active_menu': 'appointment_list',
    })
    
def my_appointments(request):
    try:
        patient = request.user.patientprofile
        all_appointments = AppointmentRequest.objects.filter(
            patient=patient
        ).order_by('slot_datetime')
        
        now = tz.now()
        
        DAYS_KO = ['월', '화', '수', '목', '금', '토', '일']
        
        def add_ampm(appointments):
            result = []
            for a in appointments:
                local_dt = tz.localtime(a.slot_datetime)
                day_of_week = DAYS_KO[local_dt.weekday()]
                result.append({
                    'obj': a,
                    'local_dt': local_dt,
                    'ampm': '오전' if local_dt.hour < 12 else '오후',
                    'date_str': f"{local_dt.year}년 {local_dt.month}월 {local_dt.day}일 ({day_of_week})",
                })
            return result
                
        upcoming = add_ampm(all_appointments.filter(slot_datetime__gte=now, status='confirmed'))
        past = add_ampm(all_appointments.filter(models.Q(slot_datetime__lt=now) | models.Q(status='cancelled')))
        
    except:
        upcoming = []
        past = []
    
    return render(request, 'appointments/appointment_my.html', {
        'upcoming': upcoming,
        'past': past,
        'active_group': 'appointments',
        'active_menu': 'my_appointments',
    })

def cancel_appointment(request, pk):
    if request.method == 'POST':
        try:
            patient = request.user.patientprofile
            appointment = AppointmentRequest.objects.get(pk=pk, patient=patient)
            
            # 하루 전까지만 취소 가능
            # 예약 당일 자정(00:00) 이전까지 취소 가능
            appointment_date = tz.localtime(appointment.slot_datetime).date()
            today = tz.localtime(tz.now()).date()
            if appointment_date > today:
                appointment.status = 'cancelled'
                appointment.save()
        except:
            pass
    
    return redirect('appointments:my_appointments')
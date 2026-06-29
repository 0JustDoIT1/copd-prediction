from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import datetime
from .models import AppointmentRequest
from accounts.models import PatientProfile
from django.db import transaction, IntegrityError
from django.utils import timezone as tz
from datetime import timedelta

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
    })


def appointment_confirm(request):
    selected_date = request.GET.get('date', '')
    selected_time = request.GET.get('time', '')
    request.session['selected_date'] = selected_date
    request.session['selected_time'] = selected_time
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
        'selected_date': selected_date,
        'selected_time': selected_time,
        'patient': patient,
        'ampm': ampm,
    })


def appointment_done(request):
    if request.method == 'POST':
        date_str = request.POST.get('date', '')
        time_str = request.POST.get('time', '')
        note = request.POST.get('note', '')
        
        try:
            # 주의: 'patientprofile'이 맞는 속성명. 위 appointment_confirm과 동일 이슈.
            patient = request.user.patientprofile
        except PatientProfile.DoesNotExist:
            patient = None
        
        try:
            slot_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y년 %m월 %d일 %H:%M")
            slot_datetime = timezone.make_aware(slot_datetime)
            
            with transaction.atomic():
                if AppointmentRequest.objects.select_for_update().filter(
                    slot_datetime=slot_datetime,
                    status = 'confirmed'
                ).exists():
                    return render(request, 'appointments/appointment_confirm.html', {
                        'selected_date': date_str,
                        'selected_time': time_str,
                        'patient': patient,
                        'error': '이미 예약된 시간입니다. 다른 시간을 선택해주세요.',
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
                'selected_time': time_str,
                'patient': patient,
                'error': '이미 예약된 시간입니다. 다른 시간을 선택해주세요.',
            })
        except Exception as e:
            print(f"예약 저장 오류: {e}")
        
        request.session.pop('selected_date', None)
        request.session.pop('selected_time', None)
        request.session['appointment_date'] = date_str
        request.session['appointment_time'] = time_str
        return redirect('appointments:appointment_done')
    
    date_str = request.session.get('appointment_date', '')
    time_str = request.session.get('appointment_time', '')
    hour = int(time_str.split(':')[0]) if time_str else 0
    ampm = '오전' if hour < 12 else '오후'
    
    return render(request, 'appointments/appointment_done.html', {
        'date': date_str,
        'time': time_str,
        'ampm': ampm,
    })


def appointment_list(request):
    appointments = AppointmentRequest.objects.select_related(
        'patient__user'
    ).order_by('slot_datetime')
    
    return render(request, 'appointments/appointment_list.html', {
        'appointments': appointments,
    })
    
def my_appointments(request):
    try:
        patient = request.user.patientprofile
        all_appointments = AppointmentRequest.objects.filter(
            patient=patient
        ).order_by('slot_datetime')
        
        now = tz.now()
        
        def add_ampm(appointments):
            result = []
            for a in appointments:
                local_dt = tz.localtime(a.slot_datetime)
                result.append({
                    'obj': a,
                    'local_dt': local_dt,
                    'ampm': '오전' if local_dt.hour < 12 else '오후',
                    'date_str': local_dt.strftime('%Y-%m-%d'),    
                })
            return result
        
        upcoming = add_ampm(all_appointments.filter(slot_datetime__gte=now))
        past = add_ampm(all_appointments.filter(slot_datetime__lt=now))
        
    except:
        upcoming = []
        past = []
    
    return render(request, 'appointments/appointment_my.html', {
        'upcoming': upcoming,
        'past': past,
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
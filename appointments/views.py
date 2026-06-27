from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import datetime
from .models import AppointmentRequest

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
    return render(request, 'appointments/appointment_request.html', {
        'slot_times_am': SLOT_TIMES_AM,
        'slot_times_pm': SLOT_TIMES_PM,
        'slot_times_sat': SLOT_TIMES_SAT,
    })

def appointment_confirm(request):
    selected_date = request.GET.get('date', '')
    selected_time = request.GET.get('time', '')
    
    try:
        patient = request.user.patient_profile
    except:
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
            patient = request.user.patient_profile
            slot_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y년 %m월 %d일 %H:%M")
            slot_datetime = timezone.make_aware(slot_datetime)
            
            AppointmentRequest.objects.create(
                patient=patient,
                slot_datetime=slot_datetime,
                note=note,
                status='confirmed',
            )
        except Exception as e:
            print(f"예약 저장 오류: {e}")
        
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
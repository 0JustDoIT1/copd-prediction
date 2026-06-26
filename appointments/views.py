from django.shortcuts import render
from datetime import datetime, timedelta, date
import calendar

SLOT_TIMES = [
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
    "16:00", "16:30", "17:00", "17:30",
]

def appointment_request(request):
    return render(request, 'appointments/appointment_request.html', {
        'slot_times': SLOT_TIMES,
    })

def appointment_confirm(request):
    return render(request, 'appointments/appointment_confirm.html')

def appointment_done(request):
    return render(request, 'appointments/appointment_done.html')
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, time
from .forms import SimpleRegisterForm, AppointmentForm
from .models import Appointment

#This is our dictionary for service minutes
SERVICE_MINUTES = {
    "Extraction": 30,
    "Spray Tan": 45,
    "Hair Removal": 60,
    "Chemical Peel": 30,
    "Acne Treatment": 45,
}

#This is our open and closing times for the business that we use to validate hours of operation
open_time = time(9, 0)
close_time = time(17, 0)

#Only open on weekdays, no weekends
open_days = [0, 1, 2, 3, 4]


def _format_time_label(time_value):
    return datetime.strptime(time_value, "%H:%M").strftime("%I:%M %p")


def get_available_time_slots(date_value, service_name, exclude_appointment_id=None):
    service_minutes = SERVICE_MINUTES.get(service_name, 30)
    existing_appointments = Appointment.objects.filter(date=date_value)

    if exclude_appointment_id:
        existing_appointments = existing_appointments.exclude(id=exclude_appointment_id)

    slots = []
    current = datetime.combine(date_value, open_time)

    while current.time() < close_time:
        end_datetime = current + timedelta(minutes=service_minutes)
        start_time = current.time()
        end_time = end_datetime.time()

        if end_time >= close_time:
            current += timedelta(minutes=15)
            continue

        overlaps = any(
            start_time < existing.endtime and end_time > existing.starttime
            for existing in existing_appointments
        )

        if not overlaps:
            slot_value = start_time.strftime("%H:%M")
            slots.append({"value": slot_value, "label": _format_time_label(slot_value)})

        current += timedelta(minutes=15)

    return slots


@login_required
def available_times(request):
    date_string = request.GET.get("date")
    service_name = request.GET.get("service")
    exclude_id = request.GET.get("exclude_id")

    if not date_string or not service_name:
        return JsonResponse({"times": []})

    try:
        selected_date = datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"times": []})

    if selected_date.weekday() not in open_days:
        return JsonResponse({"times": []})

    try:
        exclude_id = int(exclude_id) if exclude_id else None
    except ValueError:
        exclude_id = None

    slots = get_available_time_slots(selected_date, service_name, exclude_id)
    return JsonResponse({"times": slots})


def home(request):
    return render(request, "scheduler/home.html")


def login_page(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect("home")
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "scheduler/login.html", {"form": form})


def register_page(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = SimpleRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account was created and you are logged in.")
            return redirect("home")
        messages.error(request, "Please fix the errors below.")
    else:
        form = SimpleRegisterForm()

    return render(request, "scheduler/register.html", {"form": form})


def logout_page(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out.")
    return redirect("home")


#TEMPLATE shows appointments 
@login_required
def schedule_appointment(request):
    appointments = Appointment.objects.filter(client=request.user).order_by('date', 'starttime')
    return render(request, "scheduler/schedule_appointment.html", {"appointments": appointments})

@login_required
def create_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appmt = form.save(commit=False)
            appmt.client = request.user
            
            #/ This code then calculates end time based on 
            #/ the service duration from the minutes dictionary

            service_minutes = SERVICE_MINUTES.get(appmt.service, 30)  # default to 30 minutes if service not found
            #formatted as a single object for easier use
            start_datetime = datetime.combine(appmt.date, appmt.starttime)
            #It then calculates how long the appointment will take
            appmt.endtime = (start_datetime + timedelta(minutes=service_minutes)).time()

            #Below is valid days of operation checking
            validDayTest = False
            validHourTest = False
        
            if appmt.date.weekday() not in open_days:
                messages.error(request, "Our business is only open Monday - Friday from 9:00 AM to 5:00 PM.")
                validDayTest = True
                return render(request, "scheduler/create_appointment.html", {"form": form})


            #Below is valid hours checking
            if appmt.starttime < open_time or appmt.endtime >= close_time:
                messages.error(request, "Appointments must be scheduled during business hours (9:00 AM to 5:00 PM).")
                validHourTest = True
                return render(request, "scheduler/create_appointment.html", {"form": form})


            #Below will be the validation for appointment overlap
            #and 24 hr advance booking

            overlapTest = False
        

            exisiting_appointments = Appointment.objects.filter(date=appmt.date)
            for existing in exisiting_appointments:
                if (appmt.starttime < existing.endtime and appmt.endtime > existing.starttime):
                    overlapTest = True
                    break


            advanceCheck = start_datetime < datetime.now() + timedelta(hours = 24)
    
            if overlapTest:
                messages.error(request, "This appointment overlaps with an existing appointment. Please choose a different time.")
            elif advanceCheck:
                messages.error(request, "Appointments must be booked at least 24 hours in advance.")
            else:
                appmt.save()
                messages.success(request, "Your appointment has been scheduled.")
                return redirect("schedule_appointment")
        else:
            messages.error(request, "Please fix the form errors below.")
    else:
        form = AppointmentForm()

    return render(request, "scheduler/create_appointment.html", {"form": form})

#Editing an appointment
@login_required
def edit_appointment(request, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id, client=request.user)
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found.")
        return redirect("schedule_appointment")

    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            appmt = form.save(commit=False)
            appmt.client = request.user

            service_minutes = SERVICE_MINUTES.get(appmt.service, 30)
            start_datetime = datetime.combine(appmt.date, appmt.starttime)
            appmt.endtime = (start_datetime + timedelta(minutes=service_minutes)).time()

            if appmt.date.weekday() not in open_days:
                messages.error(request, "Our business is only open Monday - Friday from 9:00 AM to 5:00 PM.")
                return render(request, "scheduler/edit_appointment.html", {"form": form, "appointment": appointment})

            if appmt.starttime < open_time or appmt.endtime >= close_time:
                messages.error(request, "Appointments must be scheduled during business hours (9:00 AM to 5:00 PM).")
                return render(request, "scheduler/edit_appointment.html", {"form": form, "appointment": appointment})

            overlap_test = False
            existing_appointments = Appointment.objects.filter(date=appmt.date).exclude(id=appointment.id)
            for existing in existing_appointments:
                if appmt.starttime < existing.endtime and appmt.endtime > existing.starttime:
                    overlap_test = True
                    break

            advance_check = start_datetime < datetime.now() + timedelta(hours=24)

            if overlap_test:
                messages.error(request, "This appointment overlaps with an existing appointment. Please choose a different time.")
            elif advance_check:
                messages.error(request, "Appointments must be booked at least 24 hours in advance.")
            else:
                appmt.save()
                messages.success(request, "Your appointment has been updated.")
                return redirect("schedule_appointment")
        else:
            messages.error(request, "Please fix the form errors below.")
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, "scheduler/edit_appointment.html", {"form": form, "appointment": appointment})

#Deleting an appointment
@login_required
def delete_appointment(request, appointment_id):
    if request.method == 'POST':
        try:
            appointment = Appointment.objects.get(id=appointment_id, client=request.user)
            appointment.delete()
            messages.success(request, "Your appointment has been deleted.")
        except Appointment.DoesNotExist:
            messages.error(request, "Appointment not found.")
    return redirect("schedule_appointment")

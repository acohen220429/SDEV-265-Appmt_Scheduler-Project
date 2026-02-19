from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from .forms import SimpleRegisterForm, AppointmentForm
from .models import Appointment
from datetime import datetime, timedelta, time # for time and day validation

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


#shows appointments
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
            validDayTest = True
            validHourTest = True
        
            if appmt.date.weekday() not in open_days:
                messages.error(request, "Our business is only open Monday - Friday from 9:00 AM to 5:00 PM.")
                validDayTest = False
                return render(request, "scheduler/create_appointment.html", {"form": form})


            #Below is valid hours checking
            if appmt.starttime < open_time or appmt.endtime >= close_time:
                messages.error(request, "Appointments must be scheduled during business hours (9:00 AM to 5:00 PM).")
                validHourTest = False
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
            elif validDayTest and validHourTest:
                messages.error(request, "Invalid Appointment Slot. Business Hours are 9:00 AM to 5:00 PM, Mon-Fri.")
            else:
                appmt.save()
                messages.success(request, "Your appointment has been scheduled.")
                return redirect("schedule_appointment")
        else:
            messages.error(request, "Please fix the form errors below.")
    else:
        form = AppointmentForm()

    return render(request, "scheduler/create_appointment.html", {"form": form})




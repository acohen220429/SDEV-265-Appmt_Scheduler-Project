"""Form definitions for authentication and appointment input."""

from django import forms
from django.contrib.auth.models import User
from datetime import datetime
from .models import Appointment

# Service options available to customers.
SERVICE_CHOICES = [
    ("Extraction", "Extraction"),
    ("Spray Tan", "Spray Tan"),
    ("Hair Removal", "Hair Removal"),
    ("Chemical Peel", "Chemical Peel"),
    ("Acne Treatment", "Acne Treatment"),
]

OPEN_HOUR = 9
CLOSE_HOUR = 17

# 15-minute appointment start increments during business hours.
TIME_CHOICES = [
    (f"{hour:02d}:{minute:02d}", datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").strftime("%I:%M %p"))
    for hour in range(OPEN_HOUR, CLOSE_HOUR)
    for minute in (0, 15, 30, 45)
]


class SimpleRegisterForm(forms.Form):
    """Minimal sign-up form for username/password registration."""
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        """Reject usernames that are already in use."""
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def save(self):
        """Create and return a new Django auth user."""
        username = self.cleaned_data["username"]
        password = self.cleaned_data["password"]
        return User.objects.create_user(username=username, password=password)


class AppointmentForm(forms.ModelForm):
    """Form for creating and editing appointments."""
    service = forms.ChoiceField(choices=SERVICE_CHOICES)
    starttime = forms.ChoiceField(
        label="Start time",
        choices=TIME_CHOICES,
    )

    class Meta:
        model = Appointment
        # User-facing fields; `client` and `endtime` are assigned in views.
        fields = ["service", "date", "starttime", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        """Normalize existing `starttime` values for edit forms."""
        super().__init__(*args, **kwargs)
        starttime = self.initial.get("starttime")
        if starttime:
            self.initial["starttime"] = starttime.strftime("%H:%M")

    def clean_starttime(self):
        """Convert selected time string into a Python `time` object."""
        starttime_value = self.cleaned_data["starttime"]
        return datetime.strptime(starttime_value, "%H:%M").time()

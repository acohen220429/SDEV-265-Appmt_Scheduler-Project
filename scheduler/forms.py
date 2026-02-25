from django import forms
from django.contrib.auth.models import User
from datetime import datetime
from .models import Appointment

SERVICE_CHOICES = [
    ("Extraction", "Extraction"),
    ("Spray Tan", "Spray Tan"),
    ("Hair Removal", "Hair Removal"),
    ("Chemical Peel", "Chemical Peel"),
    ("Acne Treatment", "Acne Treatment"),
]

OPEN_HOUR = 9
CLOSE_HOUR = 17

TIME_CHOICES = [
    (f"{hour:02d}:{minute:02d}", datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").strftime("%I:%M %p"))
    for hour in range(OPEN_HOUR, CLOSE_HOUR)
    for minute in (0, 15, 30, 45)
]


class SimpleRegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def save(self):
        username = self.cleaned_data["username"]
        password = self.cleaned_data["password"]
        return User.objects.create_user(username=username, password=password)


class AppointmentForm(forms.ModelForm):
    service = forms.ChoiceField(choices=SERVICE_CHOICES)
    starttime = forms.ChoiceField(
        label="Start time",
        choices=TIME_CHOICES,
    )

    class Meta:
        model = Appointment
        #Fields are all variables user inputs themselves
        fields = ['service', 'date', 'starttime', 'notes']
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        starttime = self.initial.get("starttime")
        if starttime:
            self.initial["starttime"] = starttime.strftime("%H:%M")

    def clean_starttime(self):
        starttime_value = self.cleaned_data["starttime"]
        return datetime.strptime(starttime_value, "%H:%M").time()

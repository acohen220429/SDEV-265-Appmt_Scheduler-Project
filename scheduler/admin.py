"""Admin registrations for scheduler models."""

from django.contrib import admin
from .models import Appointment

# Makes appointments manageable from Django admin.
admin.site.register(Appointment)

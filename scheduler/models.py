"""Database models for appointment scheduling."""

from django.db import models
from django.contrib.auth.models import User

class Appointment(models.Model):
    """Represents one booked service appointment for a client."""
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.CharField(max_length=30, default="Acne Treatment")
    date = models.DateField()
    starttime = models.TimeField()
    endtime = models.TimeField()
    # Kept as separate fields for display/sorting use in the existing app.
    creation_date = models.DateTimeField(auto_now_add=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        """Readable label used in admin and shell output."""
        return f"{self.client.username} - {self.service} on {self.date} from {self.starttime} to {self.endtime}"

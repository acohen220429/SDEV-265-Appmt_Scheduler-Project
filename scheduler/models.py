from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Appointment(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    #//service can be Nails, Hair
    service = models.CharField(max_length=30, default = "Acne Treatment")
    date = models.DateField()
    starttime = models.TimeField()
    endtime = models.TimeField()
    creation_DT = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    #This is for au

    def __str__(self):
        return f"{self.client.username} - {self.service} on {self.date} from {self.starttime} to {self.endtime}"    

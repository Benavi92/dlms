import datetime
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class EventType(models.Model):
    name = models.TextField(blank=True)
    disc = models.TextField(blank=True)


class DataEvent(models.Model):
    date = models.DateField()
    time = models.TimeField(blank=True)


class DataEventPull(models.Model):
    times = models.ManyToManyField(DataEvent)


class Event(models.Model):
    name = models.CharField(max_length=120, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_add = models.DateTimeField(auto_now_add=True)
    date_time = models.ForeignKey(DataEvent, on_delete=models.CASCADE)
    event_type = models.ForeignKey(EventType, on_delete=models.DO_NOTHING)
    text = models.TextField(blank=True)


class EventManager(models.Manager):
    def create_plan(self, event, days=0, month=0, year=0, weaks=0):
        self.create(event.name)


class EventCalendar(models.Model):
    pass
from django.db import models

from djangotoolbox.fields import DictField, ListField, EmbeddedModelField


class Location(models.Model):
    time = models.DateTimeField()
    longitude = models.DecimalField()
    latitude = models.DecimalField()
    speed = models.DecimalField()
    altitude = models.DecimalField()
    bearing = models.DecimalField()
    accuracy = models.DecimalField()


class Activity(models.Model):
    time = models.DateTimeField()
    value = models.CharField()


class Trip(models.Model):
    user_id = models.CharField()
    started_at = models.DateTimeField()
    trip = DictField()
    client_version = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    locations = ListField(EmbeddedModelField(Location), null=True)
    activities = ListField(EmbeddedModelField(Activity), null=True)

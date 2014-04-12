from django.db import models

from djangotoolbox.fields import DictField, ListField, EmbeddedModelField


class Location(models.Model):
    time = models.DateTimeField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    speed = models.FloatField()
    altitude = models.FloatField()
    bearing = models.FloatField()
    accuracy = models.FloatField()


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
    
class Point(models.Model):
    SHOP = 'SH'
    LIBRARY = 'LB'
    HOME = 'HM'
    WORK = 'WK'
    UNKNOWN = 'UN'
    POINT_TYPES = (
        (SHOP, 'Shop'),
        (LIBRARY, 'Library'),
        (HOME, 'Home'),
        (WORK, 'Work'),
        (UNKNOWN, 'Unknown'),
    )
    user_id = models.CharField()
    address = models.CharField()
    visit_frequency = models.IntegerField()
    coords = ListField()
    type = models.CharField(max_length=2,
                            choices=POINT_TYPES,
                            default=UNKNOWN)
    
    

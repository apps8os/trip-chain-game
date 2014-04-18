from django.db import models

from djangotoolbox.fields import DictField, ListField, EmbeddedModelField

import logging
logger = logging.getLogger(__name__)


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


class RoadSegment(models.Model):
    street = models.CharField()
    country = models.CharField()
    city = models.CharField()
    locations = ListField(EmbeddedModelField(Location))


class Trip(models.Model):
    user_id = models.CharField()
    started_at = models.DateTimeField()
    trip = DictField()
    client_version = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    locations = ListField(EmbeddedModelField(Location), null=True)
    activities = ListField(EmbeddedModelField(Activity), null=True)
    roads = ListField(EmbeddedModelField(RoadSegment), null=True)

    
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
    lon = models.CharField()
    lat = models.CharField()
    type = models.CharField(max_length=2,
                            choices=POINT_TYPES,
                            default=UNKNOWN)


    

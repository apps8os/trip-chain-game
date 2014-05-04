from django.db import models

from djangotoolbox.fields import DictField, ListField, EmbeddedModelField

import logging
logger = logging.getLogger(__name__)


class Address(models.Model):
    city = models.CharField()
    country = models.CharField()
    county = models.CharField()
    street = models.CharField()
    label = models.CharField()
    state = models.CharField()
    district = models.CharField()
    postal_code = models.CharField()
    house_number = models.CharField(null=True)


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
    addresses = ListField(EmbeddedModelField(Address), null=True)


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
    SCHOOL = 'SC'
    POINT_TYPES = (
        (SHOP, 'Shop'),
        (LIBRARY, 'Library'),
        (HOME, 'Home'),
        (WORK, 'Work'),
        (SCHOOL, 'School'),
        (UNKNOWN, 'Unknown'),
    )
    user_id = models.CharField()
    address = models.CharField()
    visit_frequency = models.IntegerField()
    lon = models.CharField()
    lat = models.CharField()
    type = models.CharField(max_length=2,
                            choices=POINT_TYPES,
                            default=UNKNOWN)
    
    def __str__(self):
        str = "%s (%s), %s\n" % (self.address, self.type, self.visit_frequency)
        return str

class SecondaryPoint(models.Model):
    analysis_date = models.DateTimeField(auto_now_add=True, null=True)
    user_id = models.CharField()
    address = models.CharField()
    visit_frequency = models.IntegerField()
    coords = ListField()
    
    def __str__(self):
        str = "%s (%s), %s\n" % (self.address, self.coords, self.visit_frequency)
        return str
    
class AnalysisInfo(models.Model):
    analysis_date = models.DateTimeField(null=True)
    user_id = models.CharField()
    def __str__(self):
        str = "%s (%s)\n" % (self.analysis_date, self.user_id)
        return str
    

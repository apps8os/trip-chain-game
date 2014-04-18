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
    lon = models.CharField()
    lat = models.CharField()
    type = models.CharField(max_length=2,
                            choices=POINT_TYPES,
                            default=UNKNOWN)
    
    def save(self, address, type, coords, visits, user_id, lon, lat):
        self.address = address
        self.coords = coords
        if len(type) <= 0:
            type = UNKNOWN
        self.type = type
        self.visit_frequency = visits
        self.user_id = user_id
        self.lon = lon
        self.lat = lat
        
        logger.warn("Saving a point: address=%s, coords=%s, type=%s, visits=%s, lon=%s, lat=%s" % (str(address), 
                                                                                                       str(coords), 
                                                                                                       str(type), 
                                                                                                       str(visits), 
                                                                                                       str(lon), 
                                                                                                       str(lat)))
        
        super(Point, self).save()

    

import logging
import json

'''
    A class dedicated to work on place recognition logic.
'''
#Logging
logger = logging.getLogger(__name__)

class Feature:
    def __init__(self):
        #init vars
        self._coords = []
        self._type = ""
        self._km = 0.00
        self._co2 = 0.00
        self._calories = 0.00
        self._speed = 0.00
        self._time = ""
        self._activity = ""
        self._type_of_transport = ""
        
    def get_coords(self):
        return self._coords
    
    def set_coords(self, coords):
        self._coords = coords
        
    def get_type(self):
        return self._type
    
    def set_type(self, type):
        self._type = type
        
    def get_km(self):
        return self._km
    
    def set_km(self, km):
        self._km = km
        
    def get_co2(self):
        return self._co2
    
    def set_co2(self, c02):
        self._co2 = co2
        
    def get_calories(self):
        return self._calories
    
    def set_calories(self, calories):
        self._calories = calories
        
    def get_time(self):
        return self._time
    
    def set_time(self, time):
        self._time = time
        
    def get_speed(self):
        return self._speed
    
    def set_speed(self, speed):
        self._speed = speed
        
    def get_activity(self):
        return self._activity
    
    def set_activity(self, activity):
        self._activity = activity
        
    def get_transport(self):
        return self._activity
    
    def set_transport(self, activity):
        self._activity = activity
        
    def __len__(self):
        return len(self._address)
    
    def __eq__(self, other):
        return self.get_address() == other.get_address()
    
    def __str__(self):
        str = "%s (%s km in %s), %s" % (self.get_type(), self.get_km(), self.get_time(), self.get_activity())
        return str
    
    def generate_geojson(self):
        geos = []
        features = []
        poly = {
                'type': self._type,
                'coordinates': self._coords,
        }
        geos.append(poly)
        
        props = {
            'activity': self._activity,
            'time': self._time,
            'distance': self._km,
            'calories': self._calories,
            'co2': self._co2,
        }
        
        geometries = {
            'geometries': geos,
            'type': 'Feature',
            'properties' : props
                      }
        features.append(geometries)
        
        return features
    
    def find_element(self, element):
        try:
            index_element=self._coords.index(element)
            return index_element
        except ValueError:
            return -1
    
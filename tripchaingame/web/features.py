import logging
import json
from feature import Feature

'''
    A class dedicated to work on place recognition logic.
'''
#Logging
logger = logging.getLogger(__name__)

class Features:
    def __init__(self):
        #init vars
        self._features = []
        self._km = 0.00
        self._co2 = 0.00
        self._speed = 0.00
        self._time = ""
        self._date = ""
        
    def km(self):
        return "%.2f" % (self._km)
    def time(self):
        return "%.2f" % (self._time)
    def speed(self):
        return "%.2f" % (self._speed)
    def co2(self):
        return "%.2f" % (self._co2/1000)
        
    def get_features(self):
        return self._features
    
    def set_features(self, features):
        self._features = features
        
    def get_km(self):
        return self._km
    
    def set_km(self, km):
        self._km = km
        
    def get_co2(self):
        return self._co2
    
    def set_co2(self, co2):
        self._co2 = co2
        
    def get_time(self):
        return self._time
    
    def set_time(self, time):
        self._time = time
        
    def get_speed(self):
        return self._speed
    
    def set_speed(self, speed):
        self._speed = speed
        
    def get_date(self):
        return self._date
    
    def set_date(self, date):
        self._date = date
        
    def __len__(self):
        return len(self.get_features())
    
    def __eq__(self, other):
        return self.get_features() == other.get_features()
    
    def _build_geojson_trip(self):
        geojson_geometry = []
        
        for feature in self.get_features():
            total = "%s;%s;%s;%s" % (self.get_km(), self.get_time(), self.get_speed(), self.get_co2())
            feature.set_trip_total_avg_properties(total)
            geojson_geometry.append(feature.generate_geojson())
        
        trip = {
                "type": "FeatureCollection", 
                "features": geojson_geometry, 
                }
        return trip
    
	def build_geometries_geojson(self):
	    geos = []
	    for feature in self.get_features():
	        geos.append(feature.generate_geojson())
	        
	    return geos
    
    def _interpret_type_of_transport(self, n, type):
        string = ""
        if (n == '1' or n == '2' or n == '4' or n == '5' or n == '7') and (type == '1' or type == '4' or type == '3' or type == '1' or type == '5' or type == '8'):
            string = "BUS"
        elif n == '1' and type == '2':
            string = "TRAM"
        elif type == '12' or type == '13' or n == '3':
            string = "TRAIN"
        elif n == '6':
            string = "ERR: not in use"
        elif type == '6':
            string = "METRO"
        elif type == '7':
            string = "FERRY"
        else:
            return 0
        return string
    
    def _is_number(self, s):
        try:
            float(s) # for int, long and float
        except ValueError:
            try:
                complex(s) # for complex
            except ValueError:
                return False
    
        return True
    
    def _process_reittiopas_results_to_features(self,segments):
        #Array of routes, get route
        avg_km = ""
        avg_speed = ""
        avg_co2 = 0.00
        avg_time = ""
        features = []
        #route
        if segments != None and len(segments) > 0:
            if "length" in segments:
                length = str(segments["length"])
                avg_km = float(float(length) / 1000)
            if "duration" in segments:
                time = str(segments["duration"])
                avg_time = float(float(time) / 3600)
                avg_speed = float(avg_km / avg_time)
            for segment in segments["legs"]:
                feature = Feature()
                feature.set_type("LineString")
                #set up feature coords
                if "locs" in segment:
                    #coordinates nodes
                    coords = []
                    for node in segment["locs"]:
                        c = []
                        x=""
                        y=""
                        if "coord" in node:
                            coord = node["coord"]
                            if "x" in coord:
                                x = coord["x"]
                                c.append(x)
                            if "y" in coord:
                                y = coord["y"]
                                c.append(y)
                        coords.append(c)
                    feature.set_coords(coords)
                if "type" in segment:
                    act = segment["type"]
                    activity = ""
                    if act == "walk":
                        activity = "on-foot"
                    elif self._is_number(act) == True:
                        activity = "in-vehicle"
                    else:
                        activity = "unknown"
                    feature.set_activity(activity)
                if "length" in segment:
                    length = str(segment["length"])
                    kms = float(float(length) / 1000)
                    feature.set_km(kms)
                if "duration" in segment:
                    time = str(segment["duration"])
                    hours = float(float(time) / 3600)
                    speed = float(feature.get_km() / hours)
                    feature.set_speed(speed)
                    feature.set_time(hours)
                if "code" in segment:
                    code = str(segment["code"])
                    if len(code) > 1:
                        transport = code[1:]
                        type = self._interpret_type_of_transport(code[0], segment["type"])
                        if transport != "" and type != "":
                            feature.set_transport(transport)
                            feature.set_transport_type(type)
                features.append(feature)
                avg_co2 = avg_co2 + float(feature.get_co2())
            #recorde trip route
        self.set_features(features)
        self.set_km(avg_km)
        self.set_time(avg_time)
        self.set_speed(avg_speed)
        self.set_co2(avg_co2)
        
        return self._build_geojson_trip()
        
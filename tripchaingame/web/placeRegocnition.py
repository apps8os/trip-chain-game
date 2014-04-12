import logging
#from tripchaingame.web.reittiopasAPI import ReittiopasAPI
from reittiopasAPI import ReittiopasAPI
from point import Point
import json

'''
    A class dedicated to work on place recognition logic.
'''
#Logging
logger = logging.getLogger(__name__)

class PlaceRecognition:
    def __init__(self):
        #init vars
        self.__count = 0
        self.__count_of_points = {}
        self.__count_of_end_points = {}
        self.__threshold=0.1
        self.__points = []
        
    def get_points(self):
        return self.__points
    
    def get_end_points(self):
        return self.__count_of_end_points
    
    def get_size_threshold(self):
        return len(self.__points)
    
    def point_analysis(self, trips):
        self.trip_point_profiler(trips)
        return self.get_points_of_interest()

    def get_points_of_interest(self):
        size = self.get_size_threshold()
        points = self.get_points()
        points_of_interest = []
        
        for point in points:
            value = float(point.get_points()) / float(size)
            point.set_threshold_value(value)
            if value >= self.__threshold:
                points_of_interest.append(point)
                
        return points_of_interest
    
    def find_element(self, element):
        try:
            index_element=self.__points.index(element)
            return index_element
        except ValueError:
            return -1
        
    '''
        Calculates how many times user has used a particular point 
    '''

                
    def get_first_point(self, coords):
        point = self.check_trip_points(coords)
        if len(point.get_address()) > 0:
            index = self.find_element(point)
            if index > 0:
                self.__points[index].append()
            else:
                point.append()
                self.__points.append(point)

    def trip_point_profiler(self,trips):
        for t in trips:
            trip = t.trip
            geo_json_trips = json.dumps(trip)
            items = json.loads(geo_json_trips)
            for item in items["features"]:
                tyyppi = item['geometry']['type']
                if tyyppi == "LineString":
                    coords = item["geometry"]["coordinates"]
                    self.get_first_point(coords)
                    break
            else:
                continue            
            
    '''
        Iterates through coordinates of a trip array and fetches the first point information
        @param trip: array of coordinates for the trip
    '''   
    def check_trip_points(self, trip):
        
        for i,coordinates in enumerate(trip):
            if isinstance(coordinates, list):
                coords = "%s,%s" % (coordinates[0],coordinates[1])
                if i == 0:
                    start_point=self.get_point_information(coords)
                    return start_point
                        
                logger.warn("Returning empty start point, check your coordinates %s in index %d" % (coords, i))
                    
        return Point()
    
    '''
        Retrieves the wanted point information for a point
        NOTE: coordinates must be in (wgs84) format: latitude,longitude
        @param coordinates: string coordinates
    '''
    def get_point_information(self, coordinates):
        reittiopas = ReittiopasAPI()
        result = reittiopas.get_reverse_geocode(coordinates)
        result.set_coords(coordinates)
        return result
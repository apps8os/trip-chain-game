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
                self.__points[index].add_point()
                self.__points[index].set_coords(point.pop_coords())
                logger.debug("Point (%s) exists, incremented counter" % self.__points[index])
            else:
                point.add_point()
                self.__points.append(point)
                logger.debug("New point (%s)" % point)


    def get_last_location(self, feature_array, last):
        last = last+1
        wrapper = []
        for i in reversed(xrange(last)):
            logger.warn("%d / %d : %s\n" % (i, last, feature_array[i]))
            tyyppi = feature_array[i]['geometry']['type']
            if tyyppi == "LineString" or tyyppi == "Point":
                coords = feature_array[i]["geometry"]["coordinates"]
                #logger.warn(coords)
                print (tyyppi)
                
                if len(coords) > 0:
                    if tyyppi == "Point":
                        #l = list(reversed(coords))
                        wrapper.append(coords)
                        print("Wrapped up: %s" % coords)
                        if len(wrapper) > 0:
                            return wrapper
                    
                    return list(reversed(coords))
                
                else:
                    logger.debug("Skipped empty coords")
            else:
                logger.debug("Skipped one: %s" % tyyppi)
                
    def get_first_location(self, feature_array, last):
        wrapper = []
        for i in range(0,last):
            logger.warn("%d / %d : %s\n" % (i, last, feature_array[i]))
            tyyppi = feature_array[i]['geometry']['type']
            if tyyppi == "LineString" or tyyppi == "Point":
                print (tyyppi)
                coords = feature_array[i]["geometry"]["coordinates"]
                
                if tyyppi == "Point":
                    wrapper.append(coords)
                    print("Wrapped up: %s" % coords)
                    if len(wrapper) > 0:
                        return wrapper

                if len(coords) > 0:
                    return coords

    def trip_point_profiler(self,trips):
        logger.debug("trips = %d" % len(trips))
        for t in trips:
            array = {}
            trip = t.trip
            geo_json_trips = json.dumps(trip)
            items = json.loads(geo_json_trips)
            feature_array = items["features"]
            
            last = len(feature_array)-1
            if len(feature_array) > 0:
                #logger.debug("len = %d, data size = %d " % (last,len(feature_array)))
                                
                if len(feature_array) > 1:
                    node = self.get_first_location(feature_array, last)
                    if node != None:
                        array[0] = node
                    else:
                        logger.debug("Got None")
                    node = self.get_last_location(feature_array, last)
                    if node != None:
                        array[1] = node
                        logger.debug("End Point: %s" % node)
                    else:
                        logger.debug("Got None")
                else:
                    item = feature_array[0]
                    coords = item["geometry"]["coordinates"]
                    if len(coords) > 0:
                        logger.debug("Due to small size %d take only start point " % len(feature_array))
                        array[0] = coords
                        if len(coords) > 1:
                            l = list(reversed(coords))
                            #logger.debug("Reversed coords: %s " % l)
                            array[1] = l
                    else:
                        logger.debug("Skipped a point, no coordinated %s" % coords)
                    
                    
                    
                #logger.warn(array)
                for item in array.keys():
                    #logger.warn(item)
                    self.get_first_point(array[item])
                        #tyyppi = item['geometry']['type']
                        #if tyyppi == "LineString":
                        #    coords = item["geometry"]["coordinates"]
                        #    self.get_first_point(coords)
            
#                 for item in array:
#                     
#                     tyyppi = item['geometry']['type']
#                     if tyyppi == "LineString":
#                         coords = item["geometry"]["coordinates"]
#                         self.get_first_point(coords)
                        #break
                #else:
                #    continue            
            
    '''
        Iterates through coordinates of a trip array and fetches the first point information
        @param trip: array of coordinates for the trip
    '''   
    def check_trip_points(self, trip):
        #logger.debug(trip)
        for i,coordinates in enumerate(trip):
            logger.debug("Indefication of %s" % coordinates)
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
        #result.set_coords(coordinates)
        return result
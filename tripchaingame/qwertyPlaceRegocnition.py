import logging
#from tripchaingame.web.reittiopasAPI import ReittiopasAPI
#mport ReittiopasAPI
from reittiopasAPI import ReittiopasAPI

'''
    A class dedicated to work on place recognition logic.
'''
#Logging
logger = logging.getLogger(__name__)

class PlaceRecognition:
    def __init__(self):
        #init vars
        self.__count_of_points = {}
        self.__count_of_end_points = {}
    
    def point_analysis(request, trips):
        logger.warn("unfinished business...")
        profiled_starts, profiled_ends = trip_point_profiler(trips)
        logger.debug(profiled_starts)
        logger.debug(profiled_ends)
            
    '''
        Calculates how many times user has used a particular point 
    '''
    def trip_point_profiler(trips):
        points = []
        
        for t in trips:
            trip = t.trip
            geo_json_trips = json.dumps(trip)
            items = json.loads(geo_json_trips)
            for item in items["features"]:
                tyyppi = item['geometry']['type']
                if tyyppi == "LineString":
                    coords = item["geometry"]["coordinates"]
                    point = check_trip_points(coords)
                    if len(point) > 0:
                        points.append(point)
                        if point in self.__count_of_points.keys():
                            count = self.__count_of_points[point]
                            self.__count_of_points[point] = count +1
                        else:
                             self.__count_of_points[point] = 1
                             
                    point = check_trip_points(reversed(coords))
                    if len(point) > 0:
                        points.append(point)
                        if point in self.__count_of_end_points.keys():
                            self.__count = count_of_end_points[point]
                            self.__count_of_end_points[point] = count +1
                        else:
                             self.__count_of_end_points[point] = 1
                 
    '''
        Iterates through coordinates of a trip array and fetches the first point information
        @param trip: array of coordinates for the trip
    '''   
    def check_trip_points(trip):
        start_point = ""
        skip_point=False
        for i,coordinates in enumerate(trip):
            if isinstance(coordinates, list):
                coords = "%s,%s" % (coordinates[0],coordinates[1])
                if i == 0:
                    start_point=get_point_information(coords)
                    return start_point
                        
                logger.warn("Returning empty start point, check your coordinates %s in index %d" % (coords, i))
                    
        return start_point
    
    '''
        Retrieves the wanted point information for a point
        NOTE: coordinates must be in (wgs84) format: latitude,longitude
        @param coordinates: string coordinates
    '''
    def get_point_information(coordinates):
        reittiopas = ReittiopasAPI()
        result = reittiopas.get_reverse_geocode(coordinates)
        return result
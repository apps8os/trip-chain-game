import logging
#from tripchaingame.web.reittiopasAPI import ReittiopasAPI
from reittiopasAPI import ReittiopasAPI
from point import LocationPoint
import json
import collections
from datetime import datetime
from ..models import Point, SecondaryPoint, AnalysisInfo, Trip

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
        self.__threshold=0.15
        
        #array of points (objects of class LocationPoint)
        self.__points = []
        
    def most_frequent_secondary_point(self, coordinates):
        lon=0
        lat=0
        if len(coordinates) > 0:
            x=collections.Counter(coordinates)
            logger.debug(x.most_common())
            
            #Get first good pair of coordinates
            list = dict(x.most_common())
            for key, value in list.items():
                lonlat = key.split(",")
                lon = lonlat[0]
                lat = lonlat[1]
                #logger.debug("lon=%s,lat=%s (%s)" % (str(lon), str(lat), str(key)))
                if len(lon)>0 and len(lat)>0:
                    break
        return lon,lat
    
    def save_secondary_point(self, point, uid):
        '''
            Saves or updates a SecondaryPoint regarding the points existence. This is for all points, known or unknown.
            @param point: LocationPoint point that contains the data that is to be saved
            @param uid: user id
        '''
        p = SecondaryPoint.objects.filter(user_id=uid, address=point.get_address())
        
        if SecondaryPoint.objects.filter(user_id=uid, address=point.get_address()).exists():
            p.address=point.get_address()
            
            #Updating list of coordinates with values - this list contains all values for later analysis
            coordinates = SecondaryPoint.objects.get(user_id=uid, address=point.get_address()).coords
            coordinates.extend(point.get_coords())
            #p.coords=coordinates
            
            #p.visit_frequency=point.get_points()
            #analysis = AnalysisInfo.objects.filter(user_id=uid)
            #analysis.update(analysis_date = date)
            #
            return p.update(visit_frequency=point.get_points(), coords=coordinates)
        else:
            p = SecondaryPoint(address=point.get_address(), 
                      coords=point.get_coords(), 
                      visit_frequency=point.get_points(), 
                      user_id=uid)
            return p.save()
    def save_point(self, point, uid):
        '''
            Saves or updates a point regarding the points existence. Doesn't update point's type.
            @param point: LocationPoint point that contains the data that is to be saved
            @param uid: user id
        '''
        lon = 0
        lat = 0
            
        p = Point.objects.filter(user_id=uid, address=point.address)
        
        #get primary lon, lat - that is the most frequently user coordinates
        coordinates = SecondaryPoint.objects.get(user_id=uid, address=point.address).coords
        lon, lat = self.most_frequent_secondary_point(coordinates)
        
        if Point.objects.filter(user_id=uid, address=point.address).exists():
            
            #p.address=point.address
            
            #p.visit_frequency=point.visit_frequency
            #p.lon=lon
            #p.lat=lat
            return p.update(visit_frequency=point.visit_frequency, lon=lon, lat=lat)
        else:
            p = Point(address=point.address, 
                      visit_frequency=point.visit_frequency, 
                      user_id=uid, lon=lon, lat=lat, type='UN')
            return p.save()

    def save_analysis_info(self, uid):
        '''
            Saves the data of last analysis into the data model.
            @param uid: user id
        '''
        analys = AnalysisInfo.objects.filter(user_id=uid)
        
        if analys:
            i = datetime.now()
            date = i.strftime('%Y-%m-%d %H:%M:%S') #default format '%Y-%m-%d %H:%M:%S'
            analysis = AnalysisInfo.objects.filter(user_id=uid)
            analysis.update(analysis_date = date)
            return None
        else:
            i = datetime.now()
            date = i.strftime('%Y-%m-%d %H:%M:%S') #default format '%Y-%m-%d %H:%M:%S'
            analysis = AnalysisInfo(user_id=uid, analysis_date = date)
            return analysis.save()
        
    def get_points(self):
        return self.__points
    
    def get_end_points(self):
        return self.__count_of_end_points
    
    def get_size_threshold(self):
        return len(self.__points)
    
    def point_analysis(self, trips, user_id):
        self.trip_point_profiler(trips)
        return self.save_location_points(user_id)

    def save_location_points(self, user_id):
        '''
        Get's points of interest and saves them into the db. Completes analysis by updating or creating a timestamp.
        '''
        
        size = self.get_size_threshold()
        points = self.get_points()
        secondary_points_of_interest = []
        points_of_interest = []
        
        for point in points:
            res = self.save_secondary_point(point, user_id)
            logger.debug("saved a secondary point %s" % str(res) )
            secondary_points_of_interest.append(point)
            
        points_of_interest = self.get_points_of_interest(user_id)
        
        if len(points_of_interest) > 0 or len(secondary_points_of_interest) > 0:
            self.save_analysis_info(user_id)
            logger.debug("Saved analysis info secondary points %d, primary points %d" % (len(points_of_interest), len(secondary_points_of_interest)))
        
        if len(points_of_interest) > 0:
            logger.info("Stored primary points of interest")
            return points_of_interest
        else:
            logger.info("Stored secondary points of interest only")
            return secondary_points_of_interest

    def get_points_of_interest(self, user_id):
        '''
        Get's points of interest and saves them into the db
        '''
        
        total_visits = 0
        points = SecondaryPoint.objects.filter(user_id=user_id)
        for p in points:
            total_visits = total_visits+p.visit_frequency
            
        points_of_interest = []
        
        for point in points:
            value = float(point.visit_frequency) / float(total_visits)
            #point.set_threshold_value(value)
            logger.debug("Threshold equation %.2f (value) >= %.2f (threshold) for %s" % (value, self.__threshold, point.address))
            if value >= self.__threshold:
                res = self.save_point(point, user_id)
                logger.debug("saved as a primary point %s" % str(point) )
                points_of_interest.append(point)
                
        return points_of_interest
    
    def find_element(self, element):
        try:
            index_element=self.__points.index(element)
            return index_element
        except ValueError:
            return -1
        

    def get_first_point(self, coords):
        '''
        Calculates how many times user has used a particular point by saving new point objects into array of point objects.
        In case the point already exits appending new point's coordinates into the point's array of coordinates and increasing the visit frequency by one.
        '''
        point = self.check_trip_points(coords)
        if len(point.get_address()) > 0:
            index = self.find_element(point)
            if index > 0:
                self.__points[index].add_point()
                self.__points[index].set_coords(point.pop_coords())
                #logger.debug("Point (%s) exists, incremented counter" % self.__points[index])
            else:
                point.add_point()
                self.__points.append(point)
                #logger.debug("New point (%s)" % point)


    def get_last_location(self, feature_array, last):
        last = last+1
        wrapper = []
        for i in reversed(xrange(last)):
            #logger.warn("%d / %d : %s\n" % (i, last, feature_array[i]))
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
            #logger.warn("%d / %d : %s\n" % (i, last, feature_array[i]))
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
                        #logger.debug("End Point: %s" % node)
                    else:
                        logger.debug("Got None")
                else:
                    item = feature_array[0]
                    coords = item["geometry"]["coordinates"]
                    if len(coords) > 0:
                        #logger.debug("Due to small size %d take only start point " % len(feature_array))
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
            
    
    def check_trip_points(self, trip):
        '''
        Iterates through coordinates of a trip array and fetches the first point information
        @param trip: array of coordinates for the trip
        '''   
        for i,coordinates in enumerate(trip):
            #logger.debug("Indefication of %s" % coordinates)
            if isinstance(coordinates, list):
                coords = "%s,%s" % (coordinates[0],coordinates[1])
                if i == 0:
                    start_point=self.get_point_information(coords)
                    return start_point
                        
                logger.warn("Returning empty start point, check your coordinates %s in index %d" % (coords, i))
                    
        return LocationPoint()
    

    def get_point_information(self, coordinates):
        '''
        Retrieves the wanted point information for a point
        NOTE: coordinates must be in (wgs84) format: latitude,longitude
        @param coordinates: string coordinates
        '''
        reittiopas = ReittiopasAPI()
        result = reittiopas.get_reverse_geocode(coordinates)
        #result.set_coords(coordinates)
        return result
    
    def get_count_of_new_trips(self, uid):
        '''
        Returns the count of new trips since last analysis.
        @param uid: user id
        '''
        trip_count = 0
        last_analysis = None
        
        #Today's date
        date_today = self._get_todays_date()
        
        #Last analysis date
        qs = AnalysisInfo.objects.filter(user_id=uid)
        if qs.exists():
            last_analysis = qs[0]
        
        logger.debug("search %s - %s" % (date_today,str(last_analysis)))
        
        if last_analysis:
            analysis_date = last_analysis.analysis_date
            trips = Trip.objects.filter(user_id=uid,started_at__range=[analysis_date, date_today])
            trip_count = len(trips)
        else:
            #first time for everything
            self.save_analysis_info(uid)
            trips = Trip.objects.filter(user_id=uid)
            trip_count = len(trips)
            
        return trip_count
    
    def _get_todays_date(self):
        i = datetime.now()
        date_today = i.strftime('%Y-%m-%d %H:%M:%S')
        return date_today
        
        

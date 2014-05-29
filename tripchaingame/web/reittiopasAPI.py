import logging
from django.http import Http404, HttpResponse
import requests
import json
from point import LocationPoint

#Logging
logger = logging.getLogger(__name__)
import os
import datetime, time

class ReittiopasAPI:
    def __init__(self):
        #init
        self.__epsg_in='wgs84'
        self.__epsg_out='wgs84'
        self.__user=os.environ.get('REITTIOPASAPI_USER', '')
        self.__passwd=os.environ.get('REITTIOPASAPI_PASSWD', '')
        
    def get_reverse_geocode(self, coordinates):
        result = LocationPoint()
        json_response = self.execute_reverse_geocode(coordinates)
        if json_response.status_code == requests.codes.ok:
            try:
                logger.debug(json_response.url)
                r = json.dumps(json_response.json())
                routes = json.loads(r)
                for route in routes:
                    r = json.dumps(route["name"])
                    result.set_address(r.replace('"',""))
                    result.set_coords(coordinates)
            except ValueError:
                logger.debug(json_response.url)
                logger.warn("Unknown location %s" % str(coordinates))
        else:
            logger.warn(json_response.status_code)
            json_response.raise_for_status()
            
        return result
    
    def get_reverse_geocode_city(self, coordinates):
        city = ""
        json_response = self.execute_reverse_geocode(coordinates)
        if json_response.status_code == requests.codes.ok:
            try:
                logger.debug(json_response.url)
                r = json.dumps(json_response.json())
                routes = json.loads(r)
                for route in routes:
                    city = str(route["city"])
            except ValueError:
                logger.debug(json_response.url)
                logger.warn("Unknown location %s" % str(coordinates))
        else:
            logger.warn(json_response.status_code)
            json_response.raise_for_status()
            
        return city
    
    def execute_reverse_geocode(self, coordinates):
        parameters = {'request': 'reverse_geocode', 
                      'coordinate': coordinates, 
                      'epsg_in':self.__epsg_in, 
                      'epsg_out':self.__epsg_out,
                      'user':self.__user,
                      'pass': self.__passwd}
        json_response = requests.get("http://api.reittiopas.fi/hsl/prod/", params=parameters)
        return json_response
    
    def is_empty(self, string):
        if string != None:
            if string != 0:
                if len(string) > 0:
                    return False
        return True
    
    def get_geocode(self, address, city_coordinates):
        result = LocationPoint()
        parameters = {'request': 'geocode', 
                      'key': address, 
                      'loc_types': 'address',
                      'epsg_in':self.__epsg_in, 
                      'epsg_out':self.__epsg_out,
                      'user':self.__user,
                      'pass': self.__passwd}
        json_response = requests.get("http://api.reittiopas.fi/hsl/prod/", params=parameters)
        if json_response.status_code == requests.codes.ok:
            try:
                logger.debug(json_response.url)
                r = json.dumps(json_response.json())
                routes = json.loads(r)
                size = len(routes)
                if size > 1:
                    if self.is_empty(city_coordinates) == False:
                        city = self.get_reverse_geocode_city(city_coordinates)
                for route in routes:
                    r = json.dumps(route["matchedName"])
                    result.set_address(r.replace('"',""))
                    coordinates = str(route["coords"])
                    result.set_coords(coordinates)
                    if self.is_empty(city) == False and city == str(route["city"]):
                        return result
                    
            except ValueError:
                logger.debug(json_response.url)
                logger.warn("Unknown location %s" % str(address))
        else:
            logger.warn(json_response.status_code)
            json_response.raise_for_status()
            
        return result
    
    def get_route_information(self, start, end, time1,walk_cost, change_margin):
        #api.reittiopas.fi/hsl/prod/?request=route&from=2546445,6675512&to=2549445,6675513&time=1030&timetype=arrival
        result = ""
        a = time1 #.strptime(time1, "%Y-%m-%d %H:%M:%S")
        d = "%s%02d%02d" % (a.year, a.month, a.day)
        s = "%02d%02d" % (a.hour, a.minute)
        start_time = s
        start_date = int(d)
        
        logger.warn(d)
        logger.warn(s)
        
        if change_margin == 0 or change_margin == "":
            change_margin = 1.0
        
        parameters = {'request': 'route', 
                      'from': start,
                      'to': end,
                      'date': start_date,
                      'time': start_time, 
                      'walk_cost': walk_cost,
                      'change_margin': change_margin,
                      'epsg_in':self.__epsg_in, 
                      'epsg_out':self.__epsg_out,
                      'user':self.__user,
                      'pass': self.__passwd}
        json_response = requests.get("http://api.reittiopas.fi/hsl/prod/", params=parameters)
        if json_response.status_code == requests.codes.ok:
            try:
                logger.debug(json_response.url)
                result = json.loads(json.dumps(json_response.json()))
            except ValueError:
                logger.debug(json_response.url)
                logger.warn("Unknown route %s %s" % (str(start), str(end)))
        else:
            logger.debug(json_response.url)
            logger.warn(json_response.status_code)
            json_response.raise_for_status()
            
        return result
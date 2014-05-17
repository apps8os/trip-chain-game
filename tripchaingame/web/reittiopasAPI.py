import logging
from django.http import Http404, HttpResponse
import requests
import json
from point import LocationPoint

#Logging
logger = logging.getLogger(__name__)
import os

class ReittiopasAPI:
    def __init__(self):
        #init
        self.__epsg_in='wgs84'
        self.__epsg_out='wgs84'
        self.__user=os.environ.get('REITTIOPASAPI_USER', '')
        self.__passwd=os.environ.get('REITTIOPASAPI_PASSWD', '')
        
    def get_reverse_geocode(self, coordinates):
        result = LocationPoint()
        parameters = {'request': 'reverse_geocode', 
                      'coordinate': coordinates, 
                      'epsg_in':self.__epsg_in, 
                      'epsg_out':self.__epsg_out,
                      'user':self.__user,
                      'pass': self.__passwd}
        json_response = requests.get("http://api.reittiopas.fi/hsl/prod/", params=parameters)
        if json_response.status_code == requests.codes.ok:
            try:
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
    
    def get_route_information(self, start, end, coords, time1):
        #api.reittiopas.fi/hsl/prod/?request=route&from=2546445,6675512&to=2549445,6675513&time=1030&timetype=arrival
        result = ""
        parameters = {'request': 'route', 
                      'from': start,
                      'to': stop,
                      'time': time1,    
                      'epsg_in':self.__epsg_in, 
                      'epsg_out':self.__epsg_out,
                      'user':self.__user,
                      'pass': self.__passwd}
        json_response = requests.get("http://api.reittiopas.fi/hsl/prod/", params=parameters)
        if json_response.status_code == requests.codes.ok:
            try:
                result = json.dumps(json_response.json())
            except ValueError:
                logger.debug(json_response.url)
                logger.warn("Unknown route %s" % str(coordinates))
        else:
            logger.warn(json_response.status_code)
            json_response.raise_for_status()
            
        return result
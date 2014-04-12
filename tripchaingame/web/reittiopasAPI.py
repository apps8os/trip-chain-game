import logging
from django.http import Http404, HttpResponse
import requests
import json
from point import Point

#Logging
logger = logging.getLogger(__name__)

class ReittiopasAPI:
    def __init__(self):
        #init
        self.__epsg_in='wgs84'
        self.__epsg_out='wgs84'
        self.__user='tripchaingame'
        self.__passwd='nuy0Fuqu'
        
    def get_reverse_geocode(self, coordinates):
        #http://api.reittiopas.fi/hsl/prod/?request=reverse_geocode&coordinate=24.8829521,60.1995236&epsg_in=wgs84&epsg_out=wgs84&user=tripchaingame&pass=nuy0Fuqu
        result = Point()
        parameters = {'request': 'reverse_geocode', 
                      'coordinate': coordinates, 
                      'epsg_in':self.__epsg_in, 
                      'epsg_out':self.__epsg_out,
                      'user':self.__user,
                      'pass': self.__passwd}
        json_response = requests.get("http://api.reittiopas.fi/hsl/prod/", params=parameters)
        if json_response.status_code == requests.codes.ok:
            r = json.dumps(json_response.json())
            routes = json.loads(r)
            for route in routes:
                r = json.dumps(route["name"])
                result.set_address(r.replace('"',""))
                result.set_coords(coordinates)
        else:
            logger.warn(json_response.status_code)
            json_response.raise_for_status()
            
        return result
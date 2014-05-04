import logging
import json

'''
    A class dedicated to work on place recognition logic.
'''
#Logging
logger = logging.getLogger(__name__)

class LocationPoint:
    def __init__(self):
        #init vars
        self._coords = []
        self._address = ""
        self.__count_of_points = 0
        self.__threshold_value = 0
        
    def set_threshold_value(self, value):
        self.__threshold_value = value
        
    def get_threshold_value(self, value):
        return self.__threshold_value 
        
    def get_points(self):
        return self.__count_of_points
    
    def set_points(self, count):
        self.__count_of_points = count
        
    def add_point(self):
        self.__count_of_points = self.__count_of_points+1
    
    def get_coords(self):
        return self._coords
    
    def pop_coords(self):
        if len(self._coords) == 1:
            return self._coords.pop()
        else:
            return 0
    
    def set_coords(self, coordinates):
        self._coords.append(coordinates)
        #if coordinates not in self._coords:
        #    logger.warn("LocationPoint (%s) %s not found from coordinates table" % (self.get_address(),coordinates))
        #    self._coords.append(coordinates)
        #else:
        #    logger.warn("LocationPoint %s found from coordinates table" % coordinates)
    
    def get_address(self):
        return self._address
    
    def set_address(self, addr):
        self._address = addr
        
    def __len__(self):
        return len(self._address)
    
    def __eq__(self, other):
        return self.get_address() == other.get_address()
    
    def __str__(self):
        str = "%s (%s), %s\n" % (self.get_address(), self.get_coords(), self.get_points())
        return str
    
    def find_element(self, element):
        try:
            index_element=self._coords.index(element)
            return index_element
        except ValueError:
            return -1
    
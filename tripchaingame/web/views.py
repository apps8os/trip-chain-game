# coding: utf-8
from django.http import Http404, HttpResponse
import logging
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, redirect, get_object_or_404, render

from django.contrib.auth.decorators import login_required

from django.contrib.auth import logout

from django.conf import settings

import datetime, time
import json
import math

from ..models import Trip, Point, SecondaryPoint, AnalysisInfo

from tripchaingame.models import Trip

#from tripchaingame.PlaceRecognition import PlaceRecognition
from placeRecognition import PlaceRecognition
from feature import Feature
#import ..placeRecognition.PlaceRecognition

from mongoengine.django.auth import User
from social.apps.django_app.me.models import UserSocialAuth

logger = logging.getLogger(__name__)

def _uid_from_user(user):
    sa = UserSocialAuth.objects.get(user=user)
    return sa.uid

#@login_required

def home(request):
    return render_to_response('index.html')

@login_required
def locations_view(request):
    if request.user.is_authenticated():
        uid = _uid_from_user(request.user)
        #points = get_object_or_404(Point, user_id=uid)
        points = Point.objects.filter(user_id=uid)
        
        logger.debug("locations_view.is_authenticated %s" % uid)
        logger.debug("locations_view.is_authenticated %s" % points)
        
        for p in points:
            logger.debug("Point %s (%s)" % (p.address, p))
        
        locations = [str(t.address) + "<br/>" for t in points]

        return HttpResponse(locations, status=200)
    else:
        return view_trips(request)

@login_required
def route_analysis_view(request):
    context = {}
    if request.user.is_authenticated():
        places = PlaceRecognition()
        uid = _uid_from_user(request.user)
        trips = None
        last_analysis = None
        
        date_today = places._get_todays_date()
        
        #Last analysis date
        qs = AnalysisInfo.objects.filter(user_id=uid)
        if qs.exists():
            last_analysis = qs[0]
        
        logger.debug("search %s - %s" % (date_today,str(last_analysis)))
        
        if last_analysis:
            analysis_date = last_analysis.analysis_date
            trips = Trip.objects.filter(user_id=uid,started_at__range=[analysis_date, date_today])
        else:
            trips = Trip.objects.filter(user_id=_uid_from_user(request.user))
        
        #points = places.point_analysis(trips, uid)
        points = ""
        context['places'] = points
        context['uid'] = uid
        
        logger.warn("Starting trip json analysis")
        
        t = Trip.objects.filter(user_id=_uid_from_user(request.user))
        _modify_trip(t)
        
        if points != None:
            logger.debug("places = %d" % len(points))
        else:
            logger.debug("places = 0")
            
    return HttpResponse(context['places'], status=200)

def _get_places(uid):
    if uid:
        points = Point.objects.filter(user_id=uid)
        for p in points:
            logger.debug("Point %s (%s)" % (p.address, p))
        
        locations = [str(t.lon) + ";" + str(t.lat) + ";" + str(t.visit_frequency) + ";" + str(t.address) + ";" + str(t.type) for t in points]
        return locations
    else:
        return None
    
def _get_places_as_objects(uid):
    if uid:
        points = Point.objects.filter(user_id=uid)
        for p in points:
            logger.debug("Point %s (%s)" % (p.address, p))
        
        locations = points
        return locations
    else:
        return None

def save_location(request):
    ret = 0
    type = "UN"
    
    if request.method == 'POST':
        uid = request.POST['uid']
        address = request.POST['address']
        if 'type' in request.POST:
            type = request.POST['type']
            
        if len(uid) > 0 and len(address) > 0 and type != "UN":
            logger.debug("Ready to query: type=%s, address=%s, uid=%s" % (type, address, uid))
            location = Point.objects.get(user_id=uid, address=address)#get_object_or_404(Point, user_id=uid, address=address)
            if location != None:
                location.type = type
                location.save()
                #t = get_object_or_404(Point, user_id=uid, address=address)
                #logger.info("Test result: %s" % t.type)
                ret = 1
        else:
            logger.debug("Nothing saved due to bad parameters: type=%s, address=%s, uid=%s" % (type, address, uid))
    return HttpResponse(str(ret), content_type="text/plain")

def view_trips(request):
    end_postfix = "23:59:59"
    start_postfix = "00:00:00"
    context = {}
    places = PlaceRecognition()

    context['plus_scope'] = ' '.join(settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE)
    context['plus_id'] = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    
    if request.method == 'POST':
        start_date=""
        end_date=""
        if 'start_date' in request.POST and 'end_date' in request.POST:
            start_date=request.POST['start_date']
            end_date=request.POST['end_date']
            
        if 'do_cleanup' in request.POST:
            clean=request.POST['do_cleanup']
            logger.debug("Value of cleanup %s" % clean)
            if request.user.is_authenticated() and clean:
                uid = _uid_from_user(request.user)
                _clean_points(uid)
        
        context['start_date'] = start_date
        context['end_date'] = end_date
        
        if len(start_date)>0 and len(end_date)>0:
            start_date = start_date +" "+ start_postfix
            end_date = end_date +" "+ end_postfix
                
            date1 = datetime.datetime.strptime(start_date,"%m/%d/%Y %H:%M:%S")
            date2 = datetime.datetime.strptime(end_date,"%m/%d/%Y %H:%M:%S")
            
            if request.user.is_authenticated():
                uid = _uid_from_user(request.user)
                context['uid'] = uid
                context['places'] = _get_places(uid) #_get_places_as_objects
                context['places_objects'] = _get_places_as_objects(uid) #_get_places_as_objects
                trip_list = Trip.objects.filter(user_id=uid,started_at__range=[date1, date2])
                trips = [t.trip for t in trip_list]
                context['trips'] = json.dumps(trips)
                context['trip_data'] = _get_trip_data(trip_list)
                context['place_analysis'] = places.get_count_of_new_trips(uid)
            else:
                trips = [t.trip for t in Trip.objects.filter(started_at__range=[date1, date2])]
                context['trips'] = json.dumps(trips)
                context['places'] = ""
        else:
            if request.user.is_authenticated():
                uid = _uid_from_user(request.user)
                trip_list = Trip.objects.filter(user_id=uid)
                trips = [t.trip for t in trip_list]
                context['uid'] = uid
                context['trips'] = json.dumps(trips)
                context['trip_data'] = _get_trip_data(trip_list)
                context['places'] = _get_places(uid)
                context['places_objects'] = _get_places_as_objects(uid)
                context['place_analysis'] = places.get_count_of_new_trips(uid)
                
            else:
                trips = [t.trip for t in Trip.objects.all()]
                context['trips'] = json.dumps(trips)
                context['places'] = ""
    else:
        if request.user.is_authenticated():
            uid = _uid_from_user(request.user)
            trip_list = Trip.objects.filter(user_id=uid)
            trips = [t.trip for t in trip_list]
            context['uid'] = uid
            context['trips'] = json.dumps(trips)
            context['trip_data'] = _get_trip_data(trip_list)
            context['places'] = _get_places(uid)
            context['places_objects'] = _get_places_as_objects(uid)
            context['place_analysis'] = places.get_count_of_new_trips(uid)
        else:
            trips = [t.trip for t in Trip.objects.all()]
            context['trips'] = json.dumps(trips)
            context['places'] = ""
        
    return render_to_response("view_routes.html", context, context_instance=RequestContext(request))

@login_required
def trips_today(request):
    uid = _uid_from_user(request.user)
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(hours=12)

    trips = [t.trip for t in Trip.objects.filter(user_id=uid, started_at__range=[yesterday, now])]
    context = {'trips': json.dumps(trips)}
    context['uid'] = uid

    return render_to_response("view_routes.html", context)

@login_required
def my_trips(request):
    if request.user.is_authenticated():
        uid = _uid_from_user(request.user)
        
        trips = [str(t.started_at) +": <br>"+ str(t.speed)+" <br>"+ str(t.distance) + " <br>"+ str(t.trip_time) + "<br/>" + str(t.activities) + "<br/>" for t in Trip.objects.filter(user_id=uid)]
        #[['']str(t.started_at) + " " + json.dumps(t.trip) + "<br>" for t in Trip.objects.all()]
        #
        return HttpResponse(trips, status=200)
    else:
        trips = [str(t.trip) + "<br/>" for t in Trip.objects.all()]
        return HttpResponse(trips, status=200)
    
def _clean_points(uid):
    if uid:
        SecondaryPoint.objects.filter(user_id=uid).delete()
        Point.objects.filter(user_id=uid).delete()

        old_date = "01/01/1970 00:00:00"
        date = datetime.datetime.strptime(old_date,"%m/%d/%Y %H:%M:%S")
        analysis = AnalysisInfo.objects.filter(user_id=uid)
        analysis.update(analysis_date = date)
        
        #AnalysisInfo.objects.filter(user_id=uid).delete()

def login(request):
    context = {
        'plus_scope': ' '.join(settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE),
        'plus_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    }
    return render(request, 'login.html',
        context)

def logout_view(request):
    logout(request)

    return redirect('/')

def _modify_trip(trips_json):
    '''
    Add:
    - start time, end time
    - start point address, end point address
    - trip distance in km, time
    - co2 emissions
    '''
    features = []
    
    for trip in trips_json:
        #trip time
        trip_time = 0
        kms = None
        v = 0
        
        if trip.created_at != None and trip.started_at != None:
            trip_time = _calculate_trip_time(trip.started_at, trip.created_at)
        km = 0
        
        #trip distance
        t = trip.trip
        geo_json_trips = json.dumps(t)
        items = json.loads(geo_json_trips)
        feature_array = items["features"]
        if len(feature_array) > 0:
            last = len(feature_array)
            km, features = _get_location_coordinates(feature_array, last, trip.created_at, trip.started_at)
        
        for f in features:
            logger.debug(str(f))
        '''Requires first analysis of transport type and only then we can evaluate simply the co2 costs'''
        #emissions = _calculate_co2_emissions(feature_array, last)
        if trip_time != 0:
            v = _calculate_avg_speed(trip_time, km)
        
        logger.info("time=%s, km=%.5f, speed=%.2f" % (trip_time, km, v))
        
        if trip_time != 0:
            trip.trip_time=str(trip_time)
        if v != 0.00:
            trip.speed=v
        if km != 0.00:
            trip.distance = km
            
        trip.save()
        logger.info("saved %s \n" % (trip.trip_time))
            #trip.update()
    
    modified_trip_json = [t.trip for t in trips_json]
    
    return modified_trip_json


def get_trip_segment_time(feature_array, last, end_time, i, start_time):
    time = 0
    if "start_time" in feature_array[i]["properties"]:
        time1 = feature_array[i]["properties"]["start_time"]
        j = i + 1
        time2 = ""
        if j <= last:
            time2 = feature_array[j]["properties"]["start_time"]
        else:
            time2 = end_time
        if time1 != None and time2 != None:
            time = _calculate_trip_time(time1, time2)
    else:
        time1 = start_time
        time2 = end_time
        if time1 != None and time2 != None:
            time = _calculate_trip_time(time1, time2)
    return time

def _get_location_coordinates(feature_array, last, end_time, start_time):
    features = []
    present_location = None
    previous_location = None
    distance = 0.00
    segment_distances = []
    activity_distances = dict()
    ed_tyyppi = ""
    tyyppi = ""
    
    kms = float(6373)
    for i in range(0,last):
        feature = Feature()
        ed_tyyppi = tyyppi
        time, time1, time2 = "", "", ""
        speed = 0.00
        transport = ""
        co2 = 0.00
        seg_km = 0.00
        
        #Setup variables
        tyyppi = feature_array[i]['geometry']['type']
        coords = feature_array[i]["geometry"]["coordinates"]
        activity = feature_array[i]["properties"]["activity"]
        time = get_trip_segment_time(feature_array, last, end_time, i, start_time)
        
        #Setup feature
        feature.set_type(tyyppi)
        feature.set_coords(coords)
        feature.set_activity(activity)
        feature.set_time(time)
        
        if tyyppi == "LineString" or tyyppi == "Point" or tyyppi=="Feature":
            
                
            if tyyppi == "Point":
                previous_location = present_location
                present_location = coords
                if previous_location != None and present_location != None:
                    if len(present_location) > 0 and len(previous_location) > 0:
                        distance = distance + kms*_calculate_trip_distance(present_location[1], present_location[0], previous_location[1],previous_location[0])
                
            elif tyyppi == "LineString":
                seg_km = 0.00
                for coord in coords:
                    previous_location = present_location
                    present_location = coord
                    logger.info(present_location, previous_location)
                    if previous_location != None and present_location != None:
                        if len(present_location) > 0 and len(previous_location) > 0:
                            km=kms*_calculate_trip_distance(present_location[1], present_location[0], previous_location[1],previous_location[0])
                            distance = distance + km
                            if ed_tyyppi == "LineString":
                                seg_km = seg_km + km
                segment_distances.append(seg_km)
                activity_distances[activity]=seg_km
        else:
            coords = feature_array[i]["geometry"]["coordinates"]
            activity = feature_array[i]["properties"]["activity"]
            feature.set_coords(coords)
        
        feature.set_km(seg_km)
        
        if (time != "" or time != None) and (seg_km > 0.00):
            speed = _calculate_avg_speed(time, km)
        
        #Calculate afterwards    
        #if seg_km > 0.00 and activity == "in-vehicle":
       #     transport = _get_transportation_type(coords, time1, time2)
       #     co2 = _calculate_co2_emissions(transport_km, transport)

        #feature.set_transport(transport)
        #feature.set_co2(co2)        
        feature.set_speed(speed)
        
        features.append(feature)
    #logger.info("Distance %.4f km" % distance)             
    return distance, features

def build_geojson_trip(trips_json):
    
    
    trip = {
            "type": "FeatureCollection", 
            "features": features, 
            }
    return 0


'''
    //This function takes in latitude and longitude of two location and returns the distance between them as the crow flies (in km)
    function calcCrow(lat1, lon1, lat2, lon2) 
    {
      var R = 6371; // km
      var dLat = toRad(lat2-lat1);
      var dLon = toRad(lon2-lon1);
      var lat1 = toRad(lat1);
      var lat2 = toRad(lat2);

      var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.sin(dLon/2) * Math.sin(dLon/2) * Math.cos(lat1) * Math.cos(lat2); 
      var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
      var d = R * c;
      return d;
    }

    // Converts numeric degrees to radians
    function toRad(Value) 
    {
        return Value * Math.PI / 180;
    }
'''

def distance_on_unit_sphere(lat1, long1, lat2, long2):

    if lat1 == lat2 and long1 == long2:
        return 0
    
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    
    return arc

def _calculate_trip_distance(lat1, lon1, lat2, lon2):
    if lat1 == 0 or lat2 == 0 or lon1 == 0 or lon2 == 0:
        return 0
    elif lat1 == None or lat2 == None or lon1 == None or lon2 == None:
        return 0
    else:
        try:
            la1 = float(lat1)
            la2 = float(lat2)
            lo1 = float(lon1)
            lo2 = float(lon2)
            return distance_on_unit_sphere(la1, lo1, la2, lo2)
        except ValueError:
            logger.warn("Not a float")
            return 0
    

def _calculate_co2_emissions(car_km, bus_km, travelers, suomenlinna_ferry_km):
    travelers = 1
    car = (171 / travelers) * car_km
    bus = 73 * bus_km
    suomenlinna_ferry = 389 * suomenlinna_ferry_km
    
    return 0

def _calculate_calories(km, bike_km, walk_km):
    bike = 25 * bike_km
    walk = 50 * walk_km
    
    return 0

def _calculate_trip_time(time1, time2):
    date1 = datetime.datetime.strptime(str(time1).split(".")[0],"%Y-%m-%d %H:%M:%S")
    date2 = datetime.datetime.strptime(str(time2).split(".")[0],"%Y-%m-%d %H:%M:%S")
    elapsedTime = date2 - date1
    time = str(datetime.timedelta(seconds=elapsedTime.seconds))
    return time

def _calculate_avg_speed(time1, distance):
    to_kmh = 3.6
    a = time.strptime(time1, "%H:%M:%S")
    s = float(datetime.timedelta(hours=a.tm_hour, minutes=a.tm_min, seconds=a.tm_sec).seconds)
    m = float(1000 * distance)
    v = (m/s) * to_kmh
    return v

def _get_trip_data(trips):
    if trips == None or len(trips) == 0: 
        return 0
    
    modified_trip_json = []
    last = len(trips)
    
    for trip in trips:
        value = "%s;%s;%s" % (str(trip.speed), str(trip.distance), trip.trip_time)
        modified_trip_json.append(str(value))
        
    return modified_trip_json

def _get_transportation_type(coords, time1, time2):
    reittiopas = ReittiopasAPI()
    if coords != None:
        size = len(coords)
        if size > 0:
            start = coords[1]
            end = coords[-1]
            result = reittiopas.get_route_information(start, end, coords, time1)
            
            if result == "":
                return "car"
            else:
                #determine public transport
                transport = ""
                
                return transport
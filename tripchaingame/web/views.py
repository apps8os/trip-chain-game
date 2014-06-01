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
from reittiopasAPI import ReittiopasAPI
from feature import Feature
from features import Features
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

def is_number(s):
    try:
        float(s) # for int, long and float
    except ValueError:
        try:
            complex(s) # for complex
        except ValueError:
            return False

    return True

def is_empty(string):
    if string != None or is_number(string) == False:
        if string != 0:
            if len(string) > 0:
                return False
    return True


def contains_coordinates(start):
    start_numeric = True
    if len(start) > 0:
        for item in start:
            if is_number(item) == False:
                start_numeric = False
    return start_numeric

def view_find_route(request):
    context = {}

    context['plus_scope'] = ' '.join(settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE)
    context['plus_id'] = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    
    if request.method == 'POST':
        start_date=""
        start_time=""
        trip_date =""
        start_place = ""
        end_place = ""
        my_place=""
        if 'trip_date' in request.POST and is_empty(request.POST['trip_date']) == False: 
            start_date=str(request.POST['trip_date'])
            if 'start_time' in request.POST and is_empty(request.POST['start_time']) == False:
                start_time=str(request.POST['start_time'])
            else:
                start_time = datetime.datetime.now().time().strftime("%H:%M:%S")
            
            trip_date=start_date
            start_date = start_date + " " +  start_time
        else:
            start_date = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            trip_date=datetime.datetime.now().strftime("%m/%d/%Y")
            start_time = datetime.datetime.now().time().strftime("%H:%M:%S")
            
        if 'start_place' in request.POST and 'end_place' in request.POST:
            start_place=str(request.POST['start_place'])
            end_place=str(request.POST['end_place'])
        if 'my_place' in request.POST:
            my_place=str(request.POST['my_place'])
            #check if numeric coordiates in form lon,lat
            #if not search location, assume that it's an address
            #in case of an error return error message
            
        context['trip_date'] = trip_date
        context['start_time'] = start_time
        
        logger.debug("Start: %s" % start_place)
        logger.debug("End: %s" % end_place)
        logger.debug("Me: %s" % my_place)
        
        if len(start_place)>0 and len(end_place)>0:
            
            date1 = datetime.datetime.strptime(start_date,"%m/%d/%Y %H:%M:%S")

            reittiopas = ReittiopasAPI()
            walk_cost=10.0
            change_margin = 1.0
            if is_empty(start_place) == False and is_empty(end_place) == False and is_empty(my_place) == False:
                
                start = start_place.split(',')
                end = end_place.split(',')
                
                
                #Get start and en locations if coordinates
                if contains_coordinates(start) == True:
                    start_location = reittiopas.get_reverse_geocode(start_place)
                else:
                    start_location = reittiopas.get_geocode(start_place, my_place)
                if contains_coordinates(end) == True:
                    end_location = reittiopas.get_reverse_geocode(end_place)
                else:
                    end_location = reittiopas.get_geocode(end_place, my_place)
                    
                logger.debug("Start point: %s" % start_location)
                logger.debug("End point: %s" % end_location)
                
                if is_empty(start_location.get_address()) == False:
                    context["start_place"] = start_location.get_address()
                else:
                    context["start_place"] = start_place
                if is_empty(end_location.get_address()) == False:
                    context["end_place"] = end_location.get_address()
                else:
                    context["end_place"] = end_place
                    
                start_coords = start_location.pop_coords()
                end_coords = end_location.pop_coords()
                
                if is_empty(start_coords) == False and is_empty(end_coords) == False:
                    #get routes from reittiopas
                    result = reittiopas.get_route_information(start_coords, end_coords, date1, walk_cost, change_margin)
                    routes, features = process_results(result)
                    context['features'] = features
                    
                    if request.user.is_authenticated():
                        #get routes from db only for authenticated
                        uid = _uid_from_user(request.user)
                        trip_list = Trip.objects.filter(user_id=uid)
                        trips = []
                        for trip in trip_list:
                            locations = trip.locations
                            if is_empty(locations) == False:
                                first, last = locations[0], locations[-1]
                                start = start_coords.split(',')
                                end = end_coords.split(',')
                                
                                slon, slat = start[0], start[-1]
                                elon, elat = end[0], end[-1]
                                
                                if (first.longitude == slon and first.latitude == slat) and (last.longitude == elon and last.latitude == elat):
                                    if is_empty(trip.detailed_trip) == False:
                                        routes.append(trip.detailed_trip)
                                        logger.debug("Trip is not empty")
                                    else:
                                        routes.append(trip.trip)
                                        logger.debug("Trip is empty")
                                
                        
                    
                    
                else:
                    routes = "{}"
                    
            
            if request.user.is_authenticated():
                places = PlaceRecognition()
                uid = _uid_from_user(request.user)
                context['uid'] = uid
                context['places'] = _get_places(uid) #_get_places_as_objects
                context['places_objects'] = _get_places_as_objects(uid) #_get_places_as_objects
                #trip_list = Trip.objects.filter(user_id=uid,started_at__range=[date1, date2])
                #trips = [t.detailed_trip for t in trip_list]
                context['new_routes'] = "{}" #json.dumps(trips)
                context['trip_data'] = 0#_get_trip_data(trip_list)
                context['place_analysis'] = places.get_count_of_new_trips(uid)
                context['trips'] = json.dumps(routes)
            else:
                context['trips'] = "{}"
                context['places'] = ""
                context['new_routes'] = "{}"
                context['trips'] = json.dumps(routes)
                context['new_routes'] = "{}" #json.dumps(trips)
        else:
            #if route search failed due to lack of parameters
            if request.user.is_authenticated():
                places = PlaceRecognition()
                uid = _uid_from_user(request.user)
                context['uid'] = uid
                context['trips'] = "{}" #json.dumps(trips)
                context['trip_data'] = 0#_get_trip_data(trip_list)
                context['places'] = _get_places(uid)
                context['places_objects'] = _get_places_as_objects(uid)
                context['place_analysis'] = places.get_count_of_new_trips(uid)
                context['new_routes'] = "{}"
            else:
                context['trips'] = "{}"
                context['places'] = ""
                context['new_routes'] = "{}"
    else:
        if request.user.is_authenticated():
            places = PlaceRecognition()
            uid = _uid_from_user(request.user)
            context['uid'] = uid
            context['places'] = _get_places(uid)
            context['places_objects'] = _get_places_as_objects(uid)
            context['place_analysis'] = places.get_count_of_new_trips(uid)
            context['trips'] = "{}" #json.dumps(trips)
            context['trip_data'] = 0#_get_trip_data(trip_list)
            context['new_routes'] = "{}"
        else:
            context['trips'] = "{}"
            context['places'] = ""
            context['new_routes'] = "{}"
        
    return render_to_response("find_route.html", context, context_instance=RequestContext(request))

@login_required
def road_segment(request):
    uid = _uid_from_user(request.user)
    trips = Trip.objects.filter(user_id=uid, client_version="0.8").order_by('-started_at')[:50]

    body = ""
    for trip in trips:
        body += "<h2>" + str(trip.started_at) + "</h2><ol>"

        if not trip.roads:
            continue

        for rs in trip.roads:
            if rs.addresses:
                body += "<li>" + rs.street + ": " \
                        + str([int(a.house_number) for a in rs.addresses if a.house_number]) \
                        + "</li>"

        body += "</ol>"

    return HttpResponse(body)

@login_required
def activities(request):
    uid = _uid_from_user(request.user)
    trips = Trip.objects.filter(user_id=uid, client_version="0.8").order_by('-started_at')[:5]

    body = ""
    for trip in trips:
        body += "<h2>" + str(trip.started_at) + "</h2><ol>"

        for a in trip.activities:
            body += "<li>" + a.value + "</li>"

        body += "</ol>"

    return HttpResponse(body)

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
def do_full_analysis_view(request):
    context = {}
    if request.user.is_authenticated():
        places = PlaceRecognition()
        uid = _uid_from_user(request.user)
        trips = None
        
        trips = Trip.objects.filter(user_id=uid)
        
        points = places.point_analysis(trips, uid)
        points = ""
        context['places'] = points
        context['uid'] = uid
        
        logger.warn("Starting trip json analysis")
        
#         trips = Trip.objects.filter(user_id=uid)
        _modify_trip(trips)
        
        if points != None:
            logger.debug("places = %d" % len(points))
        else:
            logger.debug("places = 0")
            
    return HttpResponse(context['places'], status=200)

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
        
        points = places.point_analysis(trips, uid)
        points = ""
        context['places'] = points
        context['uid'] = uid
        
        logger.warn("Starting trip json analysis")
        
#         trips = Trip.objects.filter(user_id=uid)
        _modify_trip(trips)
        
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
                trips = [t.detailed_trip for t in trip_list]
                context['trips'] = json.dumps(trips)
                context['trip_data'] = _get_trip_data(trip_list)
                context['place_analysis'] = places.get_count_of_new_trips(uid)
            else:
                trips = [t.detailed_trip for t in Trip.objects.filter(started_at__range=[date1, date2])]
                context['trips'] = json.dumps(trips)
                context['places'] = ""
        else:
            if request.user.is_authenticated():
                uid = _uid_from_user(request.user)
                trip_list = Trip.objects.filter(user_id=uid)
                trips = [t.detailed_trip for t in trip_list]
                context['uid'] = uid
                context['trips'] = json.dumps(trips)
                context['trip_data'] = _get_trip_data(trip_list)
                context['places'] = _get_places(uid)
                context['places_objects'] = _get_places_as_objects(uid)
                context['place_analysis'] = places.get_count_of_new_trips(uid)
                
            else:
                trips = [t.detailed_trip for t in Trip.objects.all()]
                context['trips'] = json.dumps(trips)
                context['places'] = ""
    else:
        if request.user.is_authenticated():
            uid = _uid_from_user(request.user)
            trip_list = Trip.objects.filter(user_id=uid)
            trips = [t.detailed_trip for t in trip_list]
            context['uid'] = uid
            context['trips'] = json.dumps(trips)
            context['trip_data'] = _get_trip_data(trip_list)
            context['places'] = _get_places(uid)
            context['places_objects'] = _get_places_as_objects(uid)
            context['place_analysis'] = places.get_count_of_new_trips(uid)
        else:
            trips = [t.detailed_trip for t in Trip.objects.all()]
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
        if bool(trip.detailed_trip) == False:
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
                km, features = _get_location_coordinates(feature_array, last, trip.created_at, trip.started_at, trip.locations)
            
            #travel mode recognition
            _do_travel_recognition(features, trip.started_at)
            
            '''Requires first analysis of transport type and only then we can evaluate simply the co2 costs'''
            emissions = _calculate_co2_emissions(features)
            
            if trip_time != 0:
                v = _calculate_avg_speed(trip_time, km)
            
            #build geojson
            totals = "%s;%s;%s;%s" % (km, trip_time, v, emissions)
            geojson = build_geojson_trip(features, totals)
            
            
            logger.info("time=%s, km=%.5f, speed=%.2f" % (trip_time, km, v))
            
            if trip_time != 0:
                trip.trip_time=str(trip_time)
            if v != 0.00:
                trip.speed=v
            if km != 0.00:
                trip.distance = km
            if geojson:
                trip.detailed_trip = geojson
            if emissions:
                trip.co2_emissions = emissions
                
            trip.save()
            logger.info("saved %s \n" % (trip.trip_time))
    
    return trips_json

def _calculate_co2_emissions(features):
    emissions = 0.00
    for feature in features:
        emissions = emissions + float(feature.get_co2())
        
    return emissions

def _do_travel_recognition(features, time):
    travels = []
    activity = ""
    start = ""
    end = ""
    leg = []
    kms = 0.00
    clean = False
    for feature in features:
        activity = feature.get_activity()

        if activity == "in-vehicle":
            clean = True
        elif activity == "on-foot" or activity == "on-bicycle":
            clean = False
            feature.set_transport_type(activity)
        
        if activity == "in-vehicle" or (activity == "still" and (clean == True)):
            leg.append(feature)
            kms = kms + feature.get_km()
        elif activity != "in-vehicle" and activity != "still":
            if len(leg) > 0 and kms > 0.2:
                travels.append(leg)
                leg = []
                kms = 0.00
    
    if travels != None:
        if len(travels)>1:
            for leg in travels:
                first = leg[0].get_coords()
                last = leg[-1].get_coords()
                
                if first != None:
                    if len(first) > 1 and leg[0].get_type() != "Point":
                        start = first[0]
                    else:
                        start = first
                else:
                    start = first
                
                if last != None and leg[-1].get_type() != "Point":
                    if len(last) > 1:
                        end = last[-1]
                    else:
                        end = last
                else:
                    end = last
                        
                
                start_point = "%s,%s" % (start[0], start[-1])
                end_point = "%s,%s" % (end[0], end[-1])
                
                logger.info("Coordinates to start %s and end %s" % (start_point, end_point))
                transport, type = _get_transportation_type(start_point, end_point, time)
                
                features = _update_feature_list(features, leg, transport, type)
                
    return features
                
                    
def _update_feature_list(features, list, transport, type):
    for item in list:
        if item in features:
            i = features.index(item)
            features[i].set_transport(transport)
            features[i].set_transport_type(type)
    return features


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

def _get_location_coordinates(feature_array, last, end_time, start_time, locations):
    features = []
    present_location = None
    previous_location = None
    distance = 0.00
    segment_distances = []
    activity_distances = dict()
    ed_tyyppi = ""
    tyyppi = ""
    first_location_index=0
    
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
        
        start_time = locations[first_location_index].time
        time = get_trip_segment_time(feature_array, last, end_time, i, start_time)

        # append first_location_index
    
        if tyyppi == 'LineString':
            first_location_index += len(coords) - 1
        else:
            # it is a point
            # and location has not changed
            pass
        
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
                    #logger.info(present_location, previous_location)
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
        
        feature.set_speed(speed)
        features.append(feature)
        
    return distance, features

def build_geojson_trip(features, totals):
    geojson_geometry = _build_geometries_geojson(features, totals)
    trip = {
            "type": "FeatureCollection", 
            "features": geojson_geometry, 
            }
    return trip

def _build_geometries_geojson(features, totals):
    geos = []
    for feature in features:
        feature.set_trip_total_avg_properties(totals)
        geos.append(feature.generate_geojson())
        
    return geos


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


def interpret_type_of_transport(n, type):
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

def _get_transportation_type(start, end, time1):
    reittiopas = ReittiopasAPI()
    walk_cost=10.0
    change_margin = 1.0
    if start != None and end != None:
        result = reittiopas.get_route_information(start, end, time1, walk_cost, change_margin)
        
        logger.debug(result)
        
        if result == "":
            return "","car"
        else:
            #determine public transport
            #trip = json.dumps(result)
            transport = ""
            code = ""
            type = ""
            for r in range(0,len(result)):
                for j in range(0,len(result[r])):
                    segments = result[r][j]
                    for segment in segments["legs"]:
                        if "code" in segment and "type" in segment and segment["type"] != "walk":
                            code = str(segment["code"])
                            if len(code) > 1:
                                transport = code[1:]
                                logger.debug("%s,%s" % (code[0], segment["type"]))
                                type = interpret_type_of_transport(code[0], segment["type"])
                                if transport != "" and type != "":
                                    return transport, type
                            
            if transport == "" and type == "":
                return "","car"                
            
            return transport, type
        
def process_results(result):
    
    trips = []
    feature_array = []
    
    for r in range(0,len(result)):
        for j in range(0,len(result[r])):
            features = Features()
            trip = features._process_reittiopas_results_to_features(result[r][j])
            trips.append(trip)
            feature_array.append(features)
            
            
    return trips, feature_array

    
    #Array of routes, get route
    '''
    type = ""
    transport_type=""
    transport=""
    
    features = []
    for r in range(0,len(result)):
        #route
        for j in range(0,len(result[r])):
            segments = result[r][j]
            if "length" in segment:
                length = str(segment["length"])
                avg_km = float(int(length) / 1000)
            if "duration" in segment:
                time = str(segment["duration"])
                hours = float(int(time) / 3600)
                avg_speed = float(feature.get_km() / hours)
            for segment in segments["legs"]:
                feature = Feature()
                feature.set_type("LineString")
                #set up feature coords
                if "locs" in segment:
                    #coordinates nodes
                    coords = []
                    for node in segment["locs"]:
                        x=""
                        y=""
                        if "coord" in node:
                            coord = node["coord"]
                            if "x" in coord:
                                x = coord["x"]
                            if "y" in coord:
                                y = coord["y"]
                            c = "%s,%s" % (x,y)
                        coords.append(c)
                    feature.set_coords(coords)
                if "type" in segment:
                    activity = segment["type"]
                    feature.set_activity(activity)
                if "length" in segment:
                    length = str(segment["length"])
                    kms = float(int(length) / 1000)
                    feature.set_km(kms)
                if "duration" in segment:
                    time = str(segment["duration"])
                    hours = float(int(time) / 3600)
                    speed = float(feature.get_km() / hours)
                    feature.set_speed(speed)
                if "code" in segment:
                    code = str(segment["code"])
                    if len(code) > 1:
                        transport = code[1:]
                        type = interpret_type_of_transport(code[0], segment["type"])
                        if transport != "" and type != "":
                            feature.set_transport(transport)
                            feature.set_transport_type(type)
                            '''

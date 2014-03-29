# coding: utf-8
from django.http import Http404, HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, redirect, get_object_or_404, render

from django.contrib.auth.decorators import login_required

from django.contrib.auth import logout

from django.conf import settings

import datetime
import json
import logging
import requests

from ..models import Trip

from tripchaingame.models import Trip

from mongoengine.django.auth import User
from social.apps.django_app.me.models import UserSocialAuth

#Logging
logger = logging.getLogger(__name__)

def _uid_from_user(user):
    sa = UserSocialAuth.objects.get(user=user)
    return sa.uid

#@login_required

def home(request):
    return render_to_response('index.html')

def view_trips(request):
    end_postfix = "23:59:59"
    start_postfix = "00:00:00"
    context = {}
    point_analysis(request)

    context['plus_scope'] = ' '.join(settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE)
    context['plus_id'] = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    
    if request.method == 'POST':
        #if request.user.is_authenticated():
            #uid = _uid_from_user(request.user)
            #trips = [t.trip for t in Trip.objects.filter(user_id=uid,started_at)]
        start_date=""
        end_date=""
        if 'start_date' in request.POST and 'end_date' in request.POST:
            start_date=request.POST['start_date']
            end_date=request.POST['end_date']
        
        context['start_date'] = start_date
        context['end_date'] = end_date
        
        if len(start_date)>0 and len(end_date)>0:
            start_date = start_date +" "+ start_postfix
            end_date = end_date +" "+ end_postfix
                
            date1 = datetime.datetime.strptime(start_date,"%m/%d/%Y %H:%M:%S")
            date2 = datetime.datetime.strptime(end_date,"%m/%d/%Y %H:%M:%S")
            
            if request.user.is_authenticated():
                trips = [t.trip for t in Trip.objects.filter(user_id=uid,started_at__range=[date1, date2])]
                context['trips'] = json.dumps(trips)
            else:
                trips = [t.trip for t in Trip.objects.filter(started_at__range=[date1, date2])]
                #trips = [t.trip for t in Trip.objects.all()]
                context['trips'] = json.dumps(trips)
        else:
            trips = [t.trip for t in Trip.objects.all()]
            context['trips'] = json.dumps(trips)
    else:
        if request.user.is_authenticated():
            uid = _uid_from_user(request.user)
            trips = [t.trip for t in Trip.objects.filter(user_id=uid)]
            '''trips = {}
            for t in Trip.objects.filter(user_id=uid):
                date = t.started_at
                if date is not None:
                     date = datetime.strptime(date,"%Y-%m-%d")
                else:
                     date = datetime.now()
                
                str=date.strftime("%B %d, %Y")
                trips[str].append(json.dumps(t.trip))
            
            context['trips'] = trips_by_date'''
            context['trips'] = json.dumps(trips)
        else:
            trips = [t.trip for t in Trip.objects.all()]
            #trips = =Trip.objects.all()
            '''
            for t in Trip.objects.all():
                date = t.started_at
                if date is not None:
                     date = datetime.strptime(date,"%Y-%m-%d")
                else:
                     date = datetime.now()
                
                str=date.strftime("%B %d, %Y")
                trips[str] = json.dumps(t.trip)
            *#'''
            context['trips'] = json.dumps(trips)
        
        ##context['alltrips']=Trip.objects.all()
            #trips = ['']str(t.started_at) + " " + json.dumps(t.trip) + "<br>" for t in Trip.objects.all()]

    return render_to_response("view_routes.html", context, context_instance=RequestContext(request))

@login_required
def trips_today(request):
    uid = _uid_from_user(request.user)
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(hours=12)

    trips = [t.trip for t in Trip.objects.filter(user_id=uid, started_at__range=[yesterday, now])]
    context = {'trips': json.dumps(trips)}

    return render_to_response("view_routes.html", context)

@login_required
def my_trips(request):
    if request.user.is_authenticated():
        uid = _uid_from_user(request.user)
        
        trips = [str(t.started_at) +" "+ str(t.trip) + "<br/>" for t in Trip.objects.filter(user_id=uid)]
        #[['']str(t.started_at) + " " + json.dumps(t.trip) + "<br>" for t in Trip.objects.all()]
        #
        return HttpResponse(trips, status=200)
    else:
        trips = [str(t.trip) + "<br/>" for t in Trip.objects.all()]
        return HttpResponse(trips, status=200)


def point_analysis(request):
    logger.warn("unfinished business...")
    if request.user.is_authenticated():
        uid = _uid_from_user(request.user)
        #trips = [t.trip for t in Trip.objects.filter(user_id=uid)]
        trips = Trip.objects.filter(user_id=uid)
        profiled_starts, profiled_ends = trip_point_profiler(trips)
        logger.debug(profiled_starts)
        logger.debug(profiled_ends)
        
'''
    Calcultaes how many times user has used a particular point 
'''
def trip_point_profiler(trips):
    points = []
    count_of_points = {}
    count_of_end_points = {}
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
                    if point in count_of_points.keys():
                        count = count_of_points[point]
                        count_of_points[point] = count +1
                    else:
                         count_of_points[point] = 1
                         
                point = check_trip_points(reversed(coords))
                if len(point) > 0:
                    points.append(point)
                    if point in count_of_end_points.keys():
                        count = count_of_end_points[point]
                        count_of_end_points[point] = count +1
                    else:
                         count_of_end_points[point] = 1
             
    return count_of_points, count_of_end_points
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
    #http://api.reittiopas.fi/hsl/prod/?request=reverse_geocode&coordinate=24.8829521,60.1995236&epsg_in=wgs84&epsg_out=wgs84&user=tripchaingame&pass=nuy0Fuqu
    result = ""
    parameters = {'request': 'reverse_geocode', 
                  'coordinate': coordinates, 
                  'epsg_in':'wgs84', 
                  'epsg_out':'wgs84',
                  'user':'tripchaingame',
                  'pass': 'nuy0Fuqu'}
    json_response = requests.get("http://api.reittiopas.fi/hsl/prod/", params=parameters)
    if json_response.status_code == requests.codes.ok:
        r = json.dumps(json_response.json())
        routes = json.loads(r)
        for route in routes:
            r = json.dumps(route["name"])
            result = r.replace('"',"")
    else:
        logger.warn(json_response.status_code)
        json_response.raise_for_status()
        
        
    return result
        

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
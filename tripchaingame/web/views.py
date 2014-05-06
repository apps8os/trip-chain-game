# coding: utf-8
from django.http import Http404, HttpResponse
import logging
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, redirect, get_object_or_404, render

from django.contrib.auth.decorators import login_required

from django.contrib.auth import logout

from django.conf import settings

import datetime
import json

from ..models import Trip, Point, SecondaryPoint, AnalysisInfo

from tripchaingame.models import Trip

#from tripchaingame.PlaceRecognition import PlaceRecognition
from placeRecognition import PlaceRecognition
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
def road_segment(request):
    uid = _uid_from_user(request.user)
    trips = Trip.objects.filter(user_id=uid, client_version="0.8").order_by('-started_at')[:5]

    body = ""
    for trip in trips:
        body += "<h2>" + str(trip.started_at) + "</h2><ol>"

        for rs in trip.roads:
            if rs.addresses:
                body += "<li>" + rs.street + ": " \
                        + str([int(a.house_number) for a in rs.addresses if a.house_number]) \
                        + "</li>"

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
        
        context['places'] = points
        context['uid'] = uid
        logger.debug("places = %d" % len(points))
            
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
                context['places'] = _get_places(uid)
                trips = [t.trip for t in Trip.objects.filter(user_id=uid,started_at__range=[date1, date2])]
                context['trips'] = json.dumps(trips)
                context['place_analysis'] = places.get_count_of_new_trips(uid)
            else:
                trips = [t.trip for t in Trip.objects.filter(started_at__range=[date1, date2])]
                context['trips'] = json.dumps(trips)
                context['places'] = ""
        else:
            if request.user.is_authenticated():
                uid = _uid_from_user(request.user)
                trips = [t.trip for t in Trip.objects.filter(user_id=uid)]
                context['uid'] = uid
                context['trips'] = json.dumps(trips)
                context['places'] = _get_places(uid)
                context['place_analysis'] = places.get_count_of_new_trips(uid)
                
            else:
                trips = [t.trip for t in Trip.objects.all()]
                context['trips'] = json.dumps(trips)
                context['places'] = ""
    else:
        if request.user.is_authenticated():
            uid = _uid_from_user(request.user)
            trips = [t.trip for t in Trip.objects.filter(user_id=uid)]
            context['uid'] = uid
            context['trips'] = json.dumps(trips)
            context['places'] = _get_places(uid)
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
        
        trips = [str(t.started_at) +" "+ str(t.trip) + "<br/>" for t in Trip.objects.filter(user_id=uid)]
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
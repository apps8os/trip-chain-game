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

from ..models import Trip, Point

from tripchaingame.models import Trip

#from tripchaingame.PlaceRecognition import PlaceRecognition
from placeRegocnition import PlaceRecognition
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
    logger.debug("locations_view")
    if request.user.is_authenticated():
        logger.debug("locations_view.is_authenticated")
        uid = _uid_from_user(request.user)
        points = Point.objects.filter(user_id=uid)
        
        logger.debug("locations_view.is_authenticated %s" % points)
        
        for p in points:
            logger.debug("Point %s (%s)" % (p.address, p))
        
        locations = [str(t.address) + "<br/>" for t in Point.objects.filter(user_id=uid)]

        return HttpResponse(locations, status=200)
    else:
        locations = [str(t) + "<br/>" for t in Point.objects.all()]
        return HttpResponse(locations, status=200)

@login_required
def route_analysis_view(request):
    context = {}
    if request.user.is_authenticated():
        places = PlaceRecognition()
        trips = Trip.objects.filter(user_id=_uid_from_user(request.user))
        points = places.point_analysis(trips, request.user)
        context['places'] = points
        #for point in points:
            #logger.debug(str(point))
        logger.debug("places = %d" % len(points))
            
    return HttpResponse(context['places'], status=200)

def view_trips(request):
    end_postfix = "23:59:59"
    start_postfix = "00:00:00"
    context = {}

    context['plus_scope'] = ' '.join(settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE)
    context['plus_id'] = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    
    if request.method == 'POST':
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
                uid = _uid_from_user(request.user)
                context['places'] = [str(p.lon) +","+ str(p.lat) for p in Point.objects.filter(user_id=uid)]
                trips = [t.trip for t in Trip.objects.filter(user_id=uid,started_at__range=[date1, date2])]
                context['trips'] = json.dumps(trips)
            else:
                trips = [t.trip for t in Trip.objects.filter(started_at__range=[date1, date2])]
                #trips = [t.trip for t in Trip.objects.all()]
                context['trips'] = json.dumps(trips)
        else:
            if request.user.is_authenticated():
                uid = _uid_from_user(request.user)
                trips = [t.trip for t in Trip.objects.filter(user_id=uid)]
                context['trips'] = json.dumps(trips)
                context['places'] = [str(p.lon) +","+ str(p.lat) for p in Point.objects.filter(user_id=uid)]
            else:
                trips = [t.trip for t in Trip.objects.all()]
                context['trips'] = json.dumps(trips)
    else:
        if request.user.is_authenticated():
            uid = _uid_from_user(request.user)
            trips = [t.trip for t in Trip.objects.filter(user_id=uid)]
            context['trips'] = json.dumps(trips)
        else:
            trips = [t.trip for t in Trip.objects.all()]
            context['trips'] = json.dumps(trips)
        
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
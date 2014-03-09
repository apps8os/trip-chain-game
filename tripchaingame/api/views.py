from django.conf.urls import patterns, include, url
from django.http import Http404, HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, redirect, get_object_or_404, render

from django.contrib.auth.decorators import login_required

from ..models import Trip

import json
import datetime

#@login_required
def hello(request):
    return HttpResponse("Hello world")

def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

def home(request):
    #return HttpResponse('index.html')
    #t = loader.get_template('index.html')
    #c = RequestContext(request, {'foo': 'bar'})
    #return HttpResponse(t.render(c),
    #    content_type="application/xhtml+xml")
    return render_to_response('index.html')


def trip(request):
    if request.method == 'POST':
        return trip_post(request)
    elif request.method == 'GET':
        trips = [str(t.started_at) + " " + json.dumps(t.trip) + "<br>" for t in Trip.objects.all()]

        return HttpResponse(trips, status=200)

    return HttpResponse(status=405)  # method not allowed



def trip_post(request):
    if request.META['CONTENT_TYPE'] != 'application/json':
        return HttpResponse(status=415)  # unsupported media type

    trip_json = json.loads(request.body)
    started_at = int(float(trip_json['startedAt'])/1000)
    datetime.datetime.fromtimestamp(started_at)

    db_trip = Trip.objects.create(
        user_id=trip_json['userId'],
        started_at=datetime.datetime.fromtimestamp(started_at),
        trip=trip_json['trip']
    )

    db_trip.save()

    for e in Trip.objects.all():
        print(e.started_at)

    return HttpResponse(status=200)

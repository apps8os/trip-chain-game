from django.conf.urls import patterns, include, url
from django.http import Http404, HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, redirect, get_object_or_404, render

from django.contrib.auth.decorators import login_required

from ..models import Trip

import json
import datetime


def trip(request):
    if request.method == 'POST':
        return _trip_post(request)

    return HttpResponse(status=405)  # method not allowed



def _trip_post(request):
    if request.META['CONTENT_TYPE'] != 'application/json':
        return HttpResponse(status=415)  # unsupported media type

    trip_json = json.loads(request.body)

    started_at_s = int(float(trip_json['startedAt'])/1000)
    started_at = datetime.datetime.fromtimestamp(started_at_s)

    client_version = trip_json.get('clientVersion', "0.3")

    db_trip = Trip.objects.create(
        user_id=trip_json['userId'],
        started_at=started_at,
        trip=trip_json['trip'],
        client_version=client_version
    )

    db_trip.save()

    return HttpResponse(status=200)

from django.conf.urls import patterns, include, url
from django.http import Http404, HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, redirect, get_object_or_404, render

from django.contrib.auth.decorators import login_required

from ..models import Trip, Location, Activity, RoadSegment

import json
import datetime
import logging

logger = logging.getLogger(__name__)


def trip(request):
    if request.method == 'POST':
        try:
            return _trip_post(request)
        except Exception as e:
            logger.debug(e)
            return HttpResponse(status=500)

    return HttpResponse(status=405)  # method not allowed


def _trip_post(request):
    if request.META['CONTENT_TYPE'] != 'application/json':
        return HttpResponse(status=415)  # unsupported media type

    trip_json = json.loads(request.body)

    d = {
        'trip': trip_json['trip'],
        'user_id': trip_json['userId']
    }

    started_at_s = float(trip_json['startedAt'])/1000
    d['started_at'] = datetime.datetime.fromtimestamp(started_at_s)

    d['client_version'] = trip_json.get('clientVersion', "0.3")

    locations = [_convert_timestamp(l) for l in trip_json.get('locations', [])]
    d['locations'] = [Location.objects.create(**l) for l in locations] or None

    activities = [_convert_timestamp(a) for a in trip_json.get('activities', [])]
    d['activities'] = [Activity.objects.create(**a) for a in activities] or None

    d['roads'] = _create_road_segments(trip_json)

    db_trip = Trip.objects.create(**d)
    db_trip.save()

    return HttpResponse(status=200)


def _convert_timestamp(o):
    """
    Converts object's timestamp from Unix Time milliseconds to datetime
    """
    ts = o['time']
    o['time'] = datetime.datetime.fromtimestamp(float(ts)/1000)
    return o

def _create_road_segments(trip_json):
    roads = trip_json.get('roads', [])
    road_models = []
    for road_segment in roads:
        d = {
            'street': road_segment.get('street'),
            'country': road_segment.get('country'),
            'city': road_segment.get('city')
        }
        locations = [_convert_timestamp(l) for l in road_segment.get('locations', [])]
        d['locations'] = [Location.objects.create(**l) for l in locations] or None
        road_models.append(RoadSegment.objects.create(**d))

    return road_models or None

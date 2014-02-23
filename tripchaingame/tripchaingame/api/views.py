from django.shortcuts import render
from django.http import Http404, HttpResponse

from ..models import Trip

import json
import datetime


def trip(request):
    if request.method != 'POST':
        return HttpResponse(status=405)  # method not allowed

    if request.META['CONTENT_TYPE'] != 'application/json':
        return HttpResponse(status=415)  # unsupported media type

    trip_json = json.loads(request.body)
    started_at = int(float(trip_json['startedAt'])/1000)
    datetime.datetime.fromtimestamp(started_at)

    db_trip = Trip.objects.create(
        client_id=trip_json['clientId'],
        started_at=datetime.datetime.fromtimestamp(started_at),
        trip=trip_json['trip']
    )

    db_trip.save()

    for e in Trip.objects.all():
        print(e.started_at)

    return HttpResponse(status=200)

from django.http import Http404, HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, redirect, get_object_or_404, render

from django.contrib.auth.decorators import login_required

from django.conf import settings

import datetime
import json

from ..models import Trip

from tripchaingame.models import Trip

from mongoengine.django.auth import User
from social.apps.django_app.me.models import UserSocialAuth

def _uid_from_user(user):
    sa = UserSocialAuth.objects.get(user=user)
    return sa.uid

#@login_required

def home(request):
    return render_to_response('index.html')

def view_trips(request):
    context = {}
    context['trips'] = []
    if request.user.is_authenticated():
        uid = _uid_from_user(request.user)
        context['trips'] = ""+json.dumps([t.trip for t in Trip.objects.filter(user_id=uid)])
    else:
        context['trips'] = ""+json.dumps([t.trip for t in Trip.objects.all()])
    #context['alltrips']=Trip.objects.all()
            #trips = ['']str(t.started_at) + " " + json.dumps(t.trip) + "<br>" for t in Trip.objects.all()]
    
    
    return render_to_response("view_routes.html", context, context_instance=RequestContext(request))

@login_required
def my_trips(request):
    if request.user.is_authenticated():
        uid = _uid_from_user(request.user)
        trips = [str(t.trip) + "<br/>" for t in Trip.objects.filter(user_id=uid)]
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

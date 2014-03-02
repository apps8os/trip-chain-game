from django.http import Http404, HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, redirect, get_object_or_404, render

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

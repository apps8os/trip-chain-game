from django.conf.urls import patterns, include, url

from web.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'api.views.home', name='home'),
    url(r'^api/', include('tripchaingame.api.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^home/$', home),
    url(r'^hello/$', hello),
    url(r'^time/$', current_datetime),
    url(r'^view/$', view_trips),
)

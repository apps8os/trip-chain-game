from django.conf.urls import patterns, include, url
from django.conf import settings
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
    url(r'^$', view_trips),
    url(r'^home/$', home),
    url(r'^today/$', trips_today),
    url(r'^my_trips/$', my_trips),
    url(r'^login/$', login),
    url(r'^places/$', route_analysis_view),
    url(r'^my_places/$', locations_view),
    url(r'^logout/$', logout_view),
    url(r'^save_location/$', save_location),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^roads', road_segment)
)


from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# for development env.
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

# for deployment
if not settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )
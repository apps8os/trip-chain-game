from views import trip

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'api.views.home', name='home'),
    # url(r'^tripchaingame/', include('tripchaingame.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^trip.json', trip),
)
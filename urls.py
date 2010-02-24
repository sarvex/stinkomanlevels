from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from stinkomanlevels.settings import MEDIA_URL

urlpatterns = patterns('',
    # Example:
    # (r'^stinkomanlevels/', include('stinkomanlevels.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # legacy media
    (r'^img/(?P<id>.+)$', redirect_to, {'url': MEDIA_URL+"img/%(id)s"}),
    (r'^oldlevels/(?P<id>.+)$', redirect_to, {'url': MEDIA_URL+"legacy-levels/%(id)s"}),
    (r'^levels/(?P<id>.+)$', redirect_to, {'url': MEDIA_URL+"levels/%(id)s"}),
    (r'^style/(?P<id>.+)$', redirect_to, {'url': MEDIA_URL+"img/%(id)s"}),
    (r'^play/externalSwf/(?P<id>.+)$', redirect_to,
        {'url': MEDIA_URL+"swf/externalSwf/%(id)s"}),
    (r'^play/objectLibrary\\.swf$', redirect_to,
        {'url': MEDIA_URL+"swf/objectLibrary.swf"}),
    (r'^play/stinkogame\\.swf$', redirect_to,
        {'url': MEDIA_URL+"swf/stinkogame.swf"}),
    (r'^common\.js$', redirect_to, {'url': MEDIA_URL+"js/common.js"}),
    (r'^robots\.txt$', redirect_to, {'url': MEDIA_URL+"/robots.txt"}),
    (r'^favicon\.ico$', redirect_to, {'url': MEDIA_URL+"/favicon.ico"}),
    (r'^style\.css$', redirect_to, {'url': MEDIA_URL+"css/style.css"}),
    (r'^StinkomanLE-9\.4\.1\.exe$', redirect_to, {'url': MEDIA_URL+"downloads/StinkomanLE-9.4.1.exe"}),


    # views
    (r'^$', 'stinkomanlevels.main.views.home'),
    (r'^browse/$', 'stinkomanlevels.main.views.browse'),
    (r'^confirm/$', 'stinkomanlevels.main.views.confirm'),
    (r'^dashboard/$', 'stinkomanlevels.main.views.dashboard'),
    (r'^download/$', direct_to_template, {'template': 'download.html'}),
    (r'^edit/(.+)/$', 'stinkomanlevels.main.views.edit'),
    (r'^login/$', 'stinkomanlevels.main.views.user_login'),
    (r'^logout/$', 'stinkomanlevels.main.views.user_logout'),
    (r'^namecheck/$', 'stinkomanlevels.main.views.namecheck'),
    (r'^play/(.+)/$', 'stinkomanlevels.main.views.play'),
    (r'^post/$', 'stinkomanlevels.main.views.post'),
    (r'^rate/$', 'stinkomanlevels.main.views.rate'),
    (r'^register/$', 'stinkomanlevels.main.views.register'),
    (r'^submit/$', 'stinkomanlevels.main.views.submit'),
    (r'^upload/$', 'stinkomanlevels.main.views.upload'),
    (r'^user/(.+)/$', 'stinkomanlevels.main.views.user'),
)


from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    (r'^$', 'mysite.mainapp.views.home'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    (r'^enter_info/(?P<course_id>\w+)$', 'mysite.mainapp.views.availability_form'),
    (r'^raw_availabilities/(?P<course_id>\w+)$', 'mysite.mainapp.views.raw_availabilities'),
)

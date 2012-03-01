from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core import serializers
from django.utils import simplejson
from django.contrib.auth.decorators import login_required

import courses

from mysite.mainapp.models import StudentAvailability

import json
import pprint
import cas
import urllib
import mysite.settings

CAS_ENDPOINT_URL = "https://login.dartmouth.edu/cas/"
WEBAPP_LOGIN_URL = "http://google.com"

def webauth(request, ticket=None):
    service_url = 'http://'+ request.get_host() + request.get_full_path() #TODO: this isnt a full url
    print service_url
    def validate(ticket):
        val_url = CAS_ENDPOINT_URL + "validate" + \
            '?service=' + urllib.quote(service_url) + \
            '&ticket=' + urllib.quote(ticket)
        r = urllib.urlopen(val_url).readlines()    # returns 2 lines
        if len(r) == 2 and re.match("yes", r[0]) != None:
            return r[1].strip()
        return None

    if ticket:
        id = validate(ticket)
        if id:
            return id
    # No valid ticket; redirect the browser to the login page to get one
    login_url = CAS_ENDPOINT_URL + 'login' \
    + '?service=' + urllib.quote(service_url)
    # return the redirect
    return HttpResponseRedirect(login_url)

def home(request):
    data = {}
    return render_to_response('index.html', data)

def raw_availabilities(request, course_id):
    relevant_availabilities = StudentAvailability.objects.filter(course_id=course_id).all()
    data = []
    for availability in relevant_availabilities:
        data.append((availability.dnd_name, availability.as_dict()))
    data = dict(data)
    the_json_str = pprint.pformat(data)
    return HttpResponse(the_json_str)

@login_required
def availability_form(request, course_id):
    print "=="
    print request.user
    print "=="
    #if request.user
    '''
    ticket_or_redirect = webauth(request, ticket=None)
    if type(ticket_or_redirect) == HttpResponseRedirect:
        return ticket_or_redirect
    dnd_name = ticket_or_redirect
    print dnd_name
    '''

    # get the  course info from the config file
    course_info = courses.courses[course_id]

    # DISPLAY THE FORM
    if request.method == 'GET':
        c = cas.CASClient(CAS_ENDPOINT_URL, WEBAPP_LOGIN_URL)
        #id = c.Authenticate(request.GET.get('ticket', None))
        id = c.Authenticate(False)
        print id


        # TODO: figure out if they're a TA
        is_ta = False

        # TODO: figure out if they're male
        is_male = True

        # TODO: get their DND name
        dnd_name = 'Alice'

        data = {
            'sections' : course_info['sections'],
            'is_ta' : is_ta,
            'is_male' : is_male,
            'dnd_name' : dnd_name,
            'action' : request.get_full_path(),
            'success' : request.GET.get('success', False),
            }
        return render_to_response('availability_form.html', data)
    # HANDLE THE FORM INPUT
    elif request.method == 'POST':
        sa = StudentAvailability()
        sa.course_id = course_id
        sa.dnd_name = request.POST['dnd_name']
        sa.is_male = request.POST['is_male']
        sa.is_ta = request.POST['is_ta']

        # TODO: get the cant be with
        cant_be_with = []

        # TODO: get the section availability
        section_availability = []
        for section in course_info['sections']:
            if section in request.POST:
                section_availability.append(section)
        section_availability_json = json.dumps(section_availability)
        sa.section_availability_ordered = section_availability_json

        sa.save()

        redirect_url = request.get_full_path() + '?success=1'
        return HttpResponseRedirect(redirect_url)

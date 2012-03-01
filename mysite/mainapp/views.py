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
import urllib
import mysite.settings
import dnd

def get_dnd_info(name):
    record = d.lookup_unique(name, 'NAME', "NICKNAME", "UID")
    return recrod

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

def dnd_name_from_token(token):
    return token.split('@')[0]

@login_required
def availability_form(request, course_id):

    # get the  course info from the config file
    course_info = courses.courses[course_id]

    # DISPLAY THE FORM
    if request.method == 'GET':

        # get their DND name
        dnd_name = dnd_name_from_token(request.user.username)

        # figure out if they're a TA
        is_ta = False
        if dnd_name in course_info['TAs']:
            is_ta = True

        data = {
            'sections' : course_info['sections'],
            'is_ta' : is_ta,
            'students' : course_info['students'],
            'dnd_name' : dnd_name,
            'action' : request.get_full_path(),
            'success' : request.GET.get('success', False),
            }
        return render_to_response('availability_form.html', data)
    # HANDLE THE FORM INPUT
    elif request.method == 'POST':
        # get their DND name
        # (we got one from post, but let's not trust it)
        dnd_name = dnd_name_from_token(request.user.username)

        sa = StudentAvailability.objects.get_or_create(dnd_name=dnd_name)[1]
        sa.course_id = course_id
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

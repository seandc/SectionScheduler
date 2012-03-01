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
    d = dnd.DNDSession()
    record = d.lookup_unique(name, 'NAME', "NICKNAME", "UID", "DEPT")
    return record

def availabilities_as_json(course_id):
    relevant_availabilities = StudentAvailability.objects.filter(course_id=course_id).all()
    data = []
    for availability in relevant_availabilities:
        data.append((availability.dnd_name, availability.as_dict()))
    data = dict(data)
    return pprint.pformat(data)

def home(request):
    return render_to_response('index.html')

@login_required
def raw_availabilities(request, course_id):
    return HttpResponse(availabilities_as_json(course_id))

@login_required
def assignment(request, course_id):
    # only let them proceed if they are a professor
    user_info = get_dnd_info(dnd_name_from_token(request.user.username))
    if not user_info['dept'] == 'Computer Science':
        return HttpResponse('you must be a prof in order to see this')

    json_availabilities = availabilities_as_json(course_id)
    



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

        sections_values = dict([(section, '') for section in course_info['sections']])

        data = {}
        prepopulate = False
        # if they have already filled in the form, prepopulate
        sa, new = StudentAvailability.objects.get_or_create(dnd_name=dnd_name)
        if not new:
            prepopulate = True
            is_male = sa.is_male
            if is_male:
                data['male_checked'] = 'checked'
                data['female_checked'] = ''
            else:
                data['female_checked'] = 'checked'
                data['male_checked'] = ''
            available_sections = json.loads(sa.section_availability_ordered)
            sections_scores = zip(available_sections, range(1,len(available_sections)+1))
            for section, score in sections_scores:
                sections_values[section] = score

            #TODO: actually prepopulate

        # figure out if they're a TA
        is_ta = False
        if dnd_name in course_info['TAs']:
            is_ta = True

        data.update({
            'course_id' : course_id,
            'sections_values' : sections_values,
            'is_ta' : is_ta,
            'students' : course_info['students'],
            'dnd_name' : dnd_name,
            'action' : request.get_full_path().split('?')[0],
            'success' : request.GET.get('success', False),
            'invalid' : request.GET.get('invalid', False),
            })
        return render_to_response('availability_form.html', data)

    # HANDLE THE FORM INPUT
    elif request.method == 'POST':
        def form_is_valid(post_data):
            if not post_data.get('is_male', False):
                return False
            if not post_data.get('is_ta', False):
                return False
            if not [section for section in request.POST if section in course_info['sections'] and request.POST[section]]:
                return False
            return True
        if not form_is_valid(request.POST):
            # tell them to re-do the form
            redirect_url = request.get_full_path() + '?invalid=1'
            return HttpResponseRedirect(redirect_url)
        # get their DND name
        # (we got one from post, but let's not trust it)
        dnd_name = dnd_name_from_token(request.user.username)
        is_ta = False
        if dnd_name in course_info['TAs']:
            is_ta = True

        sa, new = StudentAvailability.objects.get_or_create(dnd_name=dnd_name)
        sa.course_id = course_id
        sa.is_male = request.POST['is_male']
        sa.is_ta = is_ta

        # get the cant be with
        if request.POST.get('cant_be_with', False):
            cant_be_with = request.POST.getlist('cant_be_with')
            sa.cant_be_with = json.dumps(cant_be_with)

        # TODO: get the section availability
        priority_sections = []
        for section in course_info['sections']:
            priority = request.POST.get(section, '')
            if priority != '':
                priority = int(priority)
                priority_sections.append((priority, section))
        priority_sections.sort()
        section_availability = [section for priority, section in priority_sections]
        section_availability_json = json.dumps(section_availability)
        sa.section_availability_ordered = section_availability_json

        sa.save()

        redirect_url = request.get_full_path() + '?success=1'
        return HttpResponseRedirect(redirect_url)

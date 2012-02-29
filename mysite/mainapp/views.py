from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core import serializers
from django.utils import simplejson
import courses

def home(request):
    data = {}
    return render_to_response('index.html', data)

def availability_form(request, course_id):
    # get the  course info from the config file
    course_info = courses.courses[course_id]

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
        }
    return render_to_response('availability_form.html', data)

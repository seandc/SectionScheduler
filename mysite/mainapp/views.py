from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core import serializers
from django.utils import simplejson

def home(request):
    data = {}
    return render_to_response('index.html', data)

def availability_form(request, course_id):
    data = {}
    return render_to_response('availability_form.html', data)

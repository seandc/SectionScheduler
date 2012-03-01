from django.db import models
from django.contrib.auth.models import User
import json

class StudentAvailability(models.Model):
    #user = models.OneToOneField(User)
    course_id = models.CharField(max_length=9000)

    dnd_name = models.CharField(max_length=9000)
    is_male = models.BooleanField(default=True)
    is_ta = models.BooleanField(default=False)

    # non-semantic. serialized lists
    cant_be_with = models.TextField()
    section_availability_ordered = models.TextField()
    def as_dict(self):
        return {
            'is_ta' : self.is_ta,
            'is_male' : self.is_male,
            'cant_be_with' : json.loads(self.cant_be_with),
            'section_availability_ordered' : json.loads(self.section_availability_ordered),
            }

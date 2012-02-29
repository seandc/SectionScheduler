from django.db import models
from django.contrib.auth.models import User

class StudentAvailability(models.Model):
    user = models.OneToOneField(User)
    is_male = models.BooleanField(default=True)
    is_ta = models.BooleanField(default=False)

    # non-semantic. serialized lists
    cant_be_with = models.TextField()
    section_availability_ordered = models.TextField()

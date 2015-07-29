# ----------------------------------------------------------------------- #
# Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                         #
# ----------------------------------------------------------------------- #

from django.db import models

# Create your models here.
class Participant(models.Model):
	first_name = models.CharField(max_length=128)
	last_name = models.CharField(max_length=128)
	email = models.EmailField(unique=True)
	
	participate_morning = models.BooleanField(default=False)
	participate_afternoon = models.BooleanField(default=False)
	
	registration_date = models.DateTimeField(auto_now_add=True)
	check_in = models.DateTimeField(blank=True, null=True)
	
	comments = models.TextField(blank=True)

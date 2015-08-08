# ----------------------------------------------------------------------- #
# Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                         #
# ----------------------------------------------------------------------- #

from django.db import models

# Create your models here.
class Participant(models.Model):
	participant_id = models.CharField(max_length=16, primary_key=True)
	first_name = models.CharField(max_length=128)
	last_name = models.CharField(max_length=128)
	email = models.EmailField(unique=True)
	
	mailing_list = models.BooleanField(default=True)
	
	participate_morning = models.BooleanField(default=False)
	participate_afternoon = models.BooleanField(default=False)
	
	registration_date = models.DateTimeField(auto_now_add=True)
	check_in = models.DateTimeField(blank=True, null=True)
	
	comments = models.TextField(blank=True)
	
	def __str__(self):
		return str(self.first_name) + ' ' + str(self.last_name)

class AdminProperties(models.Model):
	key = models.CharField(max_length=32, primary_key=True)
	value = models.CharField(max_length=32)
	
	def __str__(self):
		return '{\'' + str(self.key) + '\': \'' + str(self.value) + '\'}'

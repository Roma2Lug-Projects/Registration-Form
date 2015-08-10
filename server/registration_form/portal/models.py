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

class Assistance(models.Model):
	PC_DESKTOP = 'dt'
	PC_LAPTOP = 'lt'
	PC_CHROMEBOOK = 'cb'
	PC_TRANSFORMER = 'tf'
	PC_OTHER = 'oo'
	PC_TYPES = (
			(PC_DESKTOP, 'Fisso'),
			(PC_LAPTOP, 'Portatile generico'),
			(PC_CHROMEBOOK, 'Chromebook'),
			(PC_TRANSFORMER, 'Trasformabile (con touchscreen)'),
	)
	
	REFUSED = '0'
	ACCEPTED = '1'
	STATUS = (
			(REFUSED, 'Rifiutata'),
			(ACCEPTED, 'Accettata'),
	)
	participant = models.OneToOneField(Participant, primary_key=True)
	pc_type = models.CharField(max_length=2, choices=PC_TYPES, default=PC_LAPTOP)
	brand = models.CharField(max_length=32)
	model = models.CharField(max_length=32, blank=True, null=True)
	cpu = models.CharField(max_length=32, blank=True, null=True)
	ram = models.CharField(max_length=32, blank=True, null=True)
	
	problem = models.TextField()
	
	preferred_time = models.TimeField(blank=True, null=True)
	acceptance = models.CharField(max_length=1, choices=STATUS, blank=True, null=True)
	accepted_time = models.TimeField(blank=True, null=True)
	estimated_mttr = models.DurationField(blank=True, null=True)
	
	def __str__(self):
		return 'Assistenza per ' + str(self.participant.first_name) + ' ' + str(self.participant.last_name)

class AdminProperty(models.Model):
	key = models.CharField(max_length=32, primary_key=True)
	value = models.CharField(max_length=32)
	
	def __str__(self):
		return '{\'' + str(self.key) + '\': \'' + str(self.value) + '\'}'

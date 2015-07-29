# ----------------------------------------------------------------------- #
# Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                         #
# ----------------------------------------------------------------------- #

from django.contrib import admin
from portal.models import Participant

# Register your models here.

class ParticipantAdmin(admin.ModelAdmin):
	fieldsets = [
		('Participant',		{'fields': ['first_name', 'last_name', 'email']}),
		('Presences',		{'fields': ['participate_morning', 'participate_afternoon']}),
		('Registration',	{'fields': ['registration_date', 'check_in']}),
		('Comments',		{'fields': ['comments',], 'classes': ['collapse']}),
	]
	
	readonly_fields = ['registration_date',]
	
	list_display = [
		'pk',
		'first_name',
		'last_name',
		'email',
		'participate_morning',
		'participate_afternoon',
		'registration_date',
		'check_in']
	
	list_filter = ['participate_morning', 'participate_afternoon', 'check_in',]
	search_fields = ['id', 'first_name', 'last_name', 'email',]
	ordering = ['id', 'registration_date', 'check_in',]


admin.site.register(Participant, ParticipantAdmin)


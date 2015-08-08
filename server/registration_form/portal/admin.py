# ----------------------------------------------------------------------- #
# Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                         #
# ----------------------------------------------------------------------- #

from django.contrib import admin
from portal.models import Participant, AdminProperties

# Register your models here.

class ParticipantAdmin(admin.ModelAdmin):
	fieldsets = [
		('Participant',		{'fields': ['first_name', 'last_name', 'email', 'mailing_list']}),
		('Presences',		{'fields': ['participate_morning', 'participate_afternoon']}),
		('Registration',	{'fields': ['registration_date', 'check_in']}),
		('Comments',		{'fields': ['comments',], 'classes': ['collapse']}),
	]
	
	readonly_fields = ['registration_date',]
	
	list_display = [
		'participant_id',
		'first_name',
		'last_name',
		'email',
		'mailing_list',
		'participate_morning',
		'participate_afternoon',
		'registration_date',
		'check_in']
	
	list_filter = ['participate_morning', 'participate_afternoon', 'check_in', 'mailing_list']
	search_fields = ['participant_id', 'first_name', 'last_name', 'email',]
	ordering = ['registration_date', 'check_in',]

admin.site.register(Participant, ParticipantAdmin)



class PropertiesAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,		{'fields': ['key', 'value']}),
	]
	
	list_display = [
		'key',
		'value',]
	
	search_fields = ['key',]
	ordering = ['key',]


admin.site.register(AdminProperties, PropertiesAdmin)

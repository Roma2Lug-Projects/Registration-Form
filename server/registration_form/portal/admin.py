# ----------------------------------------------------------------------- #
# Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                         #
# ----------------------------------------------------------------------- #

from django.contrib import admin
from portal.models import Participant, AdminProperty, Assistance



class ParticipantAdmin(admin.ModelAdmin):
	fieldsets = [
		('Participant',		{'fields': ['first_name', 'last_name', 'email', 'mailing_list']}),
		('Presences',		{'fields': ['participate_morning', 'participate_afternoon']}),
		('Registration',	{'fields': ['registration_date', 'check_in', 'tshirt']}),
		('Comments',		{'fields': ['comments',], 'classes': ['collapse']}),
	]
	
	readonly_fields = ['registration_date',]
	
	list_display = [
		'participant_id',
		'first_name',
		'last_name',
		'email',
		'tshirt',
		'mailing_list',
		'participate_morning',
		'participate_afternoon',
		'registration_date',
		'check_in']
	
	list_filter = ['participate_morning', 'participate_afternoon', 'tshirt', 'check_in', 'mailing_list']
	search_fields = ['participant_id', 'first_name', 'last_name', 'email', 'tshirt',]
	ordering = ['registration_date', 'check_in',]

admin.site.register(Participant, ParticipantAdmin)



class AssistanceAdmin(admin.ModelAdmin):
	fieldsets = [
		('Participant',		{'fields': ['participant']}),
		('PC info',			{'fields': ['pc_type', 'brand', 'model', 'cpu', 'ram', 'problem']}),
		('Time',			{'fields': ['preferred_time', 'acceptance', 'accepted_time', 'estimated_mttr']}),
		('Operator',		{'fields': ['operator']}),
	]
	
	list_display = [
		'participant',
		'pc_type',
		'problem',
		'acceptance',
		'accepted_time',
		'estimated_mttr',
		'operator',]
	
	list_filter = ['pc_type', 'acceptance']
	search_fields = ['participant']
	ordering = ['participant', 'accepted_time','operator']

admin.site.register(Assistance, AssistanceAdmin)



class PropertyAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,		{'fields': ['key', 'value']}),
	]
	
	list_display = [
		'key',
		'value',]
	
	search_fields = ['key',]
	ordering = ['key',]


admin.site.register(AdminProperty, PropertyAdmin)

# ----------------------------------------------------------------------- #
# Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                         #
# ----------------------------------------------------------------------- #

from django.conf.urls import patterns, url, include

from portal import views

urlpatterns = patterns('',
	
	# Registration form
	url(r'^$', views.index, name='index'),
	url(r'^participants$', views.participant_list, name='participants'),
	url(r'^participants/morning$', views.morning_users, name='morning_users'),
	url(r'^participants/afternoon$', views.afternoon_users, name='afternoon_users'),
	url(r'^participants/mailing_list$', views.mailing_list, name='mailing_list'),
	url(r'^participants/checked_in$', views.checked_in, name='checked_in'),
	url(r'^participants/details/(?P<participant_id>[a-z0-9]{16})$', views.participant_details, name='participant_details'),
	url(r'^emails$', views.email_sender, name='email_sender'),
	url(r'^registration$', views.admin_form, name='admin_form'),
	url(r'^query$', views.query_search, name='query_search'),
	url(r'^assistance_form$', views.assistance_form, name='assistance_form'),
	url(r'^assistances$', views.assistance_list, name='assistance_list'),
	url(r'^assistances/pending$', views.pending_assistances, name='pending_assistances'),
	url(r'^assistances/accepted$', views.accepted_assistances, name='accepted_assistances'),
	url(r'^assistances/refused$', views.refused_assistances, name='refused_assistances'),
	url(r'^assistances/served$', views.served_assistances, name='served_assistances'),
	url(r'^assistances/details/(?P<participant_id>[a-z0-9]{16})$', views.assistance_details, name='assistance_details'),
	url(r'^assistances/status/(?P<participant_id>[a-z0-9]{16})$', views.assistance_status, name='assistance_status'),
	
	# REST interfaces
	url(r'^rest/participants/$', views.RESTParticipantList.as_view(), name='rest_participants_list'),
	url(r'^rest/participants/(?P<pk>[a-z0-9]{16})/$', views.RESTParticipantDetails.as_view(), name='rest_participants_details'),
	url(r'^rest/assistances/$', views.RESTAssistanceList.as_view(), name='rest_assistances_list'),
	url(r'^rest/assistances/(?P<pk>[a-z0-9]{16})/$', views.RESTAssistanceDetails.as_view(), name='rest_assistances_details'),
	url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	
	# Access management
	url(r'^accounts/login/$', views.login, name='login'),
	url(r'^accounts/logout/$', views.logout, name='logout'),
)

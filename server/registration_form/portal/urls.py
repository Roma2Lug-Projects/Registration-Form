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
	url(r'^participants/details$', views.participant_details, name='participant_details'),
	url(r'^emails$', views.email_sender, name='email_sender'),
	url(r'^registration$', views.admin_form, name='admin_form'),
	
	# REST interfaces
	url(r'^rest/$', views.RESTParticipantList.as_view(), name='rest_list'),
	url(r'^rest/(?P<pk>[a-z0-9]{16})/$', views.RESTParticipantDetail.as_view(), name='rest_detail'),
	url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	
	# Access management
	url(r'^accounts/login/$', views.login, name='login'),
	url(r'^accounts/logout/$', views.logout, name='logout'),
)

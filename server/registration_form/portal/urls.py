# ----------------------------------------------------------------------- #
# Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                         #
# ----------------------------------------------------------------------- #

from django.conf.urls import patterns, url, include

from portal import views

urlpatterns = patterns('',
	
	# Registration form
	url(r'^$', views.index, name='index'),
	url(r'^rest/$', views.RESTParticipantList.as_view(), name='rest_list'),
	url(r'^rest/(?P<pk>[a-z0-9]{16})/$', views.RESTParticipantDetail.as_view(), name='rest_detail'),
	url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	
	# Access management
	url(r'^accounts/login/$', views.login, name='login'),
	url(r'^accounts/logout/$', views.logout, name='logout'),
)

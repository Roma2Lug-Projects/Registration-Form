# ----------------------------------------------------------------------- #
# Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                         #
# ----------------------------------------------------------------------- #

from django.conf.urls import patterns, url, include

from simple_qrcode import views

urlpatterns = patterns('',
	
	# Registration form
	url(r'^(?P<qr_id>\d+)$', views.qrview, name='qrview'),
	url(r'^dl/(?P<qr_id>\d+)\.svg$', views.qrsvg, name='qrsvg'),
	url(r'^dl/(?P<qr_id>\d+)\.png$', views.qrpng, name='qrpng'),
)

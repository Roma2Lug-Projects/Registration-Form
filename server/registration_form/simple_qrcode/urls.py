# ----------------------------------------------------------------------- #
# Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                         #
# ----------------------------------------------------------------------- #

from django.conf.urls import patterns, url, include

from simple_qrcode import views

urlpatterns = patterns('',
	
	# Registration form
	url(r'^(?P<qr_id>[a-z0-9]{16})$', views.qrview, name='qrview'),
	url(r'^dl/(?P<qr_id>[a-z0-9]{16})\.svg$', views.qrsvg, name='qrsvg'),
	url(r'^dl/(?P<qr_id>[a-z0-9]{16})\.png$', views.qrpng, name='qrpng'),
)

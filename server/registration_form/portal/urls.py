from django.conf.urls import patterns, url, include

from portal import views

urlpatterns = patterns('',
	
	# Registration form
	url(r'^$', views.index, name='index'),
	
	# Rest queries
	url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)

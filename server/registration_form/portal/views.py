# ----------------------------------------------------------------------- #
# Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                         #
# ----------------------------------------------------------------------- #

from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.crypto import get_random_string

import threading
from syslog import syslog as print
from django.conf import settings

# REST
from rest_framework import generics
from rest_framework import permissions

# Email
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage

# QR Code
import qrcode
from qrcode.image.pure import PymagingImage
from io import BytesIO

# Model
from django.db import IntegrityError
from portal.models import Participant
from portal.serializers import ParticipantSerializer



# Change this if you want to enable/disable emails service
DISABLE_EMAIL = settings.DEBUG

# Create your views here.
PARTICIPATIONS = [
	[0, 'Mattina'],
	[1, 'Pomeriggio'],
	[2, 'Mattina e pomeriggio'],
]



# Support functions and classes

def generateSerial():
	chars = '0123456789abcdefghijklmnopqrstuvwxyz'
	return get_random_string(16, chars)

def send_email(participant):
	# Generate QRCode
	img = qrcode.make(participant.participant_id, image_factory=PymagingImage)
	img_stream = BytesIO()
	img.save(img_stream, 'PNG')
	
	# Compose email
	subject = 'ID registrazione Linux Day Roma 2014'
	from_email = 'Roma2LUG <roma2lug@gmail.com>'
	
	text = 'Caro ' + participant.first_name + ',\n'
	text += 'grazie per esserti iscritto al nostro Linux Day.\n'
	text += 'Ti preghiamo di conservare questa email come promemoria e di presentarla all\'ingresso.\n\n'
	text += 'Linux Day Roma\n'
	text += '25 Ottobre 2014\n'
	text += 'Facolta\' di Ingegneria, Universita\' Tor Vergata\n'
	text += 'Via del Politecnico 1, edificio della Didattica.\n'
	text += 'ID registrazione: ' + str(participant.participant_id) + '\n\n'
	text += 'A presto,\nRoma2LUG.\n'
	
	html = '<p>Caro ' + participant.first_name + ',<br />\n'
	html += 'grazie per esserti iscritto al nostro Linux Day.<br />\n'
	html += 'Ti preghiamo di conservare questa email come promemoria e di presentarla all\'ingresso.</p>\n'
	html += '<p>Linux Day Roma<br />\n'
	html += '25 Ottobre 2014<br />\n'
	html += 'Facolta\' di Ingegneria, Universita\' Tor Vergata<br />\n'
	html += 'Via del Politecnico 1, edificio della Didattica.<br /></p>\n'
	html += '<p>ID registrazione: <b>' + str(participant.participant_id) + '</b><br />\n'
	html += '<img src="cid:qrcode"></p>\n'
	html += '<p>A presto,<br />Roma2LUG.</p>\n'
	
	# Add content to email
	mail = EmailMultiAlternatives(subject, text, from_email, [participant.email])
	mail.attach_alternative(html, 'text/html')
	image = MIMEImage(img_stream.getvalue(), 'png')
	image.add_header('Content-ID', '<qrcode>') # This is the ID used in tag <img> for HTML part of the email
	mail.attach(image)
	
	mail.send(fail_silently=True)

class RegistrationForm(forms.Form):
	
	first_name = forms.CharField(label='Nome*', max_length=128, required=True)
	last_name = forms.CharField(label='Cognome*', max_length=128, required=True)
	email = forms.EmailField(label='Email*', required=True)
	participates = forms.ChoiceField(label='Partecipazione', choices=PARTICIPATIONS, required=False)
	comments = forms.CharField(label='Commenti', max_length=512, widget=forms.Textarea, required=False)



# Views

def index(request):
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = RegistrationForm(request.POST)

		if form.is_valid():
			i = form.cleaned_data['participates']
			morning = False
			afternoon = False
			
			if i == '0':
				morning = True
			elif i == '1':
				afternoon = True
			elif i == '2':
				morning = True
				afternoon = True
			
			
			participant_id = generateSerial()
			while Participant.objects.filter(participant_id=participant_id).exists():
				participant_id = generateSerial()
			
			p = Participant(
							participant_id = participant_id,
							first_name = form.cleaned_data['first_name'],
							last_name = form.cleaned_data['last_name'],
							email = form.cleaned_data['email'],
							comments = form.cleaned_data['comments'],
							participate_morning = morning,
							participate_afternoon = afternoon
			)
			try:
				p.save()
			except IntegrityError as e:
				return render(request, 'portal/index.html', {'form': form, 'errors': True})
			
			# Send the email
			if not DISABLE_EMAIL:
				t = threading.Thread(target=send_email, args=(p,))
				t.start()
			else:
				print('Email disabled! No mail was sent to new registered user "' + form.cleaned_data['first_name'] + '".')
			
			reg_id = participant_id
			name = p.first_name
			return render(request, 'portal/result.html', {'reg_id': reg_id, 'name': name})

	else:
		form = RegistrationForm()

	return render(request, 'portal/index.html', {'form': form})



# REST Interface
class RESTParticipantList(generics.ListCreateAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	queryset = Participant.objects.all()
	serializer_class = ParticipantSerializer

class RESTParticipantDetail(generics.RetrieveUpdateDestroyAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	queryset = Participant.objects.all()
	serializer_class = ParticipantSerializer

# ----------------------------------------------------------------------- #
# Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                         #
# ----------------------------------------------------------------------- #

# Python basic libraries
import threading
from syslog import syslog as print

# Django components
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import Http404

# Authentication
import django.contrib.auth

# REST
from rest_framework import generics
from rest_framework import permissions

# Email
from django.core.mail import EmailMultiAlternatives, send_mass_mail
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
#DISABLE_EMAIL = settings.DEBUG
DISABLE_EMAIL = False



# Support functions and classes

def generateSerial():
	chars = '0123456789abcdefghijklmnopqrstuvwxyz'
	return get_random_string(16, chars)

def getUniqueParticipantID():
	participant_id = generateSerial()
	while Participant.objects.filter(participant_id=participant_id).exists():
		participant_id = generateSerial()
	return participant_id

def send_registration_email(participant):
	# Generate QRCode
	img = qrcode.make(participant.participant_id, image_factory=PymagingImage)
	img_stream = BytesIO()
	img.save(img_stream, 'PNG')
	
	# Compose email
	subject = 'ID registrazione Linux Day Roma 2014'
	from_email = settings.EMAIL_CANONICAL_NAME + ' <' + settings.EMAIL_HOST_USER + '>'
	
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

def send_email(participants, subject, message):
	from_email = settings.EMAIL_CANONICAL_NAME + ' <' + settings.EMAIL_HOST_USER + '>'
	
	email_list = []
	for p in participants:
		email = str(p) + ' <' + p.email + '>'
		email_list.append((subject, message, from_email, [email,]))
	email_tuples = tuple(email_list)
	
	send_mass_mail(email_tuples, fail_silently=True)

PARTICIPATIONS = [
	[0, 'Mattina'],
	[1, 'Pomeriggio'],
	[2, 'Mattina e pomeriggio'],
]
# Campi del form di registrazione
class RegistrationForm(forms.Form):
	first_name = forms.CharField(label='Nome*', max_length=128, required=True)
	last_name = forms.CharField(label='Cognome*', max_length=128, required=True)
	email = forms.EmailField(label='Email*', required=True)
	participates = forms.ChoiceField(label='Partecipazione', choices=PARTICIPATIONS, required=False)
	comments = forms.CharField(label='Commenti', max_length=512, widget=forms.Textarea, required=False)
	mailing_list = forms.BooleanField(label='Consenti di ricevere email riguardanti il Linux Day come variazioni sul programma o eventi speciali.', initial=True, required=False)



# Views

@require_http_methods(['GET', 'POST'])
def index(request):
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# Create a form instance and populate it with data from the request:
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
			
			participant_id = getUniqueParticipantID()
			
			p = Participant(
							participant_id = participant_id,
							first_name = form.cleaned_data['first_name'],
							last_name = form.cleaned_data['last_name'],
							email = form.cleaned_data['email'],
							mailing_list = form.cleaned_data['mailing_list'],
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
				t = threading.Thread(target=send_registration_email, args=(p,))
				t.start()
			else:
				print('Email disabled! No mail was sent to new registered user "' + form.cleaned_data['first_name'] + '".')
			
			reg_id = participant_id
			name = p.first_name
			return render(request, 'portal/result.html', {'reg_id': reg_id, 'name': name})

	else:
		# This is a GET HTTP request
		content = {}
		
		if request.user.is_authenticated():
			# Show a page summary
			registered_users = Participant.objects.count()
			content['registered_users'] = registered_users
			
			morning_users = Participant.objects.filter(participate_morning=True).count()
			content['morning_users'] = morning_users
			
			afternoon_users = Participant.objects.filter(participate_afternoon=True).count()
			content['afternoon_users'] = afternoon_users
			
			mailable_users = Participant.objects.filter(mailing_list=True).count()
			content['mailable_users'] = mailable_users
			
			seen_users = Participant.objects.filter(check_in__isnull=False).count()
			content['seen_users'] = seen_users
		
		else:
			# Show the registration form
			form = RegistrationForm()
			content['form'] = form
		
		return render(request, 'portal/index.html', content)

@require_http_methods(['GET',])
@login_required
def participant_list(request):
	participants = Participant.objects.values(
			'participant_id',
			'last_name',
			'first_name',
			'participate_morning',
			'participate_afternoon',
			'registration_date',
			'mailing_list').order_by('last_name')
	return render(request, 'portal/participant_list.html', {'participants': participants, 'message': 'Lista di tutte le persone iscritte'})

@require_http_methods(['GET',])
@login_required
def morning_users(request):
	participants = Participant.objects.filter(participate_morning=True).values(
			'participant_id',
			'last_name',
			'first_name',
			'participate_morning',
			'participate_afternoon',
			'registration_date',
			'mailing_list').order_by('last_name')
	return render(request, 'portal/participant_list.html', {'participants': participants, 'message': 'Lista degli iscritti per la mattina'})

@require_http_methods(['GET',])
@login_required
def afternoon_users(request):
	participants = Participant.objects.filter(participate_afternoon=True).values(
			'participant_id',
			'last_name',
			'first_name',
			'participate_morning',
			'participate_afternoon',
			'registration_date',
			'mailing_list').order_by('last_name')
	return render(request, 'portal/participant_list.html', {'participants': participants, 'message': 'Lista degli iscritti per il pomeriggio'})

@require_http_methods(['GET',])
@login_required
def mailing_list(request):
	participants = Participant.objects.filter(mailing_list=True).values(
			'participant_id',
			'last_name',
			'first_name',
			'participate_morning',
			'participate_afternoon',
			'registration_date',
			'mailing_list').order_by('last_name')
	return render(request, 'portal/participant_list.html', {'participants': participants, 'message': 'Lista delle persone autorizzate a ricevere email'})

@require_http_methods(['GET',])
@login_required
def checked_in(request):
	participants = Participant.objects.filter(check_in__isnull=False).values(
			'participant_id',
			'last_name',
			'first_name',
			'participate_morning',
			'participate_afternoon',
			'registration_date',
			'mailing_list').order_by('last_name')
	return render(request, 'portal/participant_list.html', {'participants': participants, 'message': 'Persone già presenti all\'evento'})

@require_http_methods(['GET',])
@login_required
def participant_details(request):
	participant_id = request.GET.get('id')
	if not participant_id:
		raise Http404('Non è stato richiesto nessun ID')
	
	participant = get_object_or_404(Participant, participant_id=participant_id)
	
	return render(request, 'portal/participant.html', {'p': participant})

@require_http_methods(['GET','POST'])
@login_required
def email_sender(request):
	if request.method == 'GET':
		participant_id = request.GET.get('id')
		if not participant_id:
			raise Http404('Non è stato richiesto nessun ID')
		if not (participant_id == 'all' or Participant.objects.filter(mailing_list=True, participant_id=participant_id).exists()):
			raise Http404('ID non valido')
		
		content = {'participant_id': participant_id,
				'from': settings.EMAIL_CANONICAL_NAME + ' <' + settings.EMAIL_HOST_USER + '>'}
		
		if participant_id == 'all':
			content['to'] = str(Participant.objects.filter(mailing_list=True).count()) + ' partecipanti'
		else:
			participant = Participant.objects.get(participant_id=participant_id)
			content['to'] = str(participant)
		
		return render(request, 'portal/emails.html', content)
	
	else:
		participant_id = request.POST['participant_id']
		subject = request.POST['subject']
		message = request.POST['message']
		
		if participant_id == 'all':
			participants = Participant.objects.filter(mailing_list=True)
			
		else:
			participants = Participant.objects.filter(mailing_list=True, participant_id=participant_id)
		
		# Send the email
		if not DISABLE_EMAIL:
			t = threading.Thread(target=send_email, args=(participants, subject, message))
			t.start()
		else:
			print('Email disabled! No mail was sent.')
		
		return render(request, 'portal/emails.html', {'confirm_message': 'L\'email è stata inviata a ' + str(len(participants)) + ' partecipanti.'})



# REST Interface
class RESTParticipantList(generics.ListCreateAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	queryset = Participant.objects.all()
	serializer_class = ParticipantSerializer

class RESTParticipantDetail(generics.RetrieveUpdateDestroyAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	queryset = Participant.objects.all()
	serializer_class = ParticipantSerializer



# System wide views

def login(request):
	if request.method == 'GET':
		if request.user.is_authenticated():
			return HttpResponseRedirect(reverse('portal:index'))
		else:
			nexturl = request.GET.get('next', '')
			return render(request, 'portal/login.html', {'next': nexturl})
	
	elif request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		nexturl = request.POST.get('next', '')
		
		user = django.contrib.auth.authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				# Registered user, log user in
				django.contrib.auth.login(request, user)
				if nexturl:
					return HttpResponseRedirect(nexturl)
				else:
					return HttpResponseRedirect(reverse('portal:index'))
					
			else:
				# Inactive user
				return render(request, 'portal/login.html', {'error_message': 'Il tuo account non &egrave attivo'})
				
		else:
			# Invalid credential
			content = {
						'error_message': 'Errore di autenticazione!',
						'username': username
			}
			return render(request, 'portal/login.html', content)

def logout(request):
	if request.user.is_authenticated():
		django.contrib.auth.logout(request)
		
	return render(request, 'portal/logout.html')

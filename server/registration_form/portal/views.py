# ----------------------------------------------------------------------- #
# Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                         #
# ----------------------------------------------------------------------- #

# Python basic libraries
import threading
from syslog import syslog as print
from datetime import datetime

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
from django.core import validators
from django.core.exceptions import ObjectDoesNotExist

# Authentication
import django.contrib.auth

# REST
from rest_framework import generics
from rest_framework import permissions

# Email
from django.core.mail import EmailMultiAlternatives, send_mass_mail, send_mail
from email.mime.image import MIMEImage

# QR Code
import qrcode
from qrcode.image.pure import PymagingImage
from io import BytesIO

# Model
from django.db import IntegrityError
from portal.models import Participant, AdminProperty, Assistance
from portal.serializers import ParticipantSerializer, AssistanceSerializer

#####################################################################################################

# Change this if you want to enable/disable emails service
DISABLE_EMAIL = settings.DEBUG
#DISABLE_EMAIL = False

#####################################################################################################

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
	subject = 'ID registrazione Linux Day Roma 2015'
	try:
		from_email = settings.EMAIL_CANONICAL_NAME + ' <' + settings.EMAIL_HOST_USER + '>'
	except AttributeError:
		from_email = settings.EMAIL_HOST_USER
	to_email = str(participant) + ' <' + participant.email + '>'
	
	text = 'Caro ' + participant.first_name + ',\n'
	text += 'grazie per esserti iscritto al nostro Linux Day.\n'
	text += 'Ti preghiamo di conservare questa email come promemoria e di mostrarla quando ti verra\' richiesto.\n\n'
	text += 'Linux Day Roma\n'
	text += '24 Ottobre 2015\n'
	text += 'Facolta\' di Ingegneria, Universita\' Tor Vergata\n'
	text += 'Via del Politecnico 1, edificio della Didattica.\n'
	text += 'ID registrazione: ' + str(participant.participant_id) + '\n\n'
	text += 'A presto,\nRoma2LUG e LugRoma3.\n'
	
	html = '<p>Caro ' + participant.first_name + ',<br />\n'
	html += 'grazie per esserti iscritto al nostro Linux Day.<br />\n'
	html += 'Ti preghiamo di conservare questa email come promemoria e di mostrarla quando ti verra\' richiesto.</p>\n'
	html += '<p><a href="http://lug.uniroma2.it/ld15/">Linux Day Roma</a><br />\n'
	html += '24 Ottobre 2015<br />\n'
	html += 'Facolta\' di Ingegneria, Universita\' Tor Vergata<br />\n'
	html += 'Via del Politecnico 1, edificio della Didattica.<br /></p>\n'
	html += '<p>ID registrazione: <b>' + str(participant.participant_id) + '</b><br />\n'
	html += '<img src="cid:qrcode"></p>\n'
	html += '<p>A presto,<br />Roma2LUG e LugRoma3.</p>\n'
	
	# Add content to email
	mail = EmailMultiAlternatives(subject, text, from_email, [to_email,])
	mail.attach_alternative(html, 'text/html')
	image = MIMEImage(img_stream.getvalue(), 'png')
	image.add_header('Content-ID', '<qrcode>') # This is the ID used in tag <img> for HTML part of the email
	mail.attach(image)
	
	mail.send(fail_silently=False)

def send_assistance_email(assistance):
	# Compose email
	subject = 'Linux Day 2015: aggiornamento stato richiesta di assistenza'
	try:
		from_email = settings.EMAIL_CANONICAL_NAME + ' <' + settings.EMAIL_HOST_USER + '>'
	except AttributeError:
		from_email = settings.EMAIL_HOST_USER
	to_email = str(assistance.participant) + ' <' + assistance.participant.email + '>'
	
	status = '--'
	for s in Assistance.STATUS:
		if s[0] == assistance.acceptance:
			status = s[1]
	
	text = 'Caro ' + assistance.participant.first_name + ',\n'
	text += 'ti informiamo che la tua richiesta di assistenza ha cambiato stato ed è stata ' + status + '.\n'
	if assistance.acceptance == Assistance.ACCEPTED:
		text += 'L\'appuntamento è stato fissato per le ' + assistance.accepted_time + '.\n'
		text += 'Ricordati di presentare la tua email di registrazione all\'ingresso e di nuovo al banchetto assistenze.\n\n'
	else:
		text += 'Per avere maggiori informazioni sul perché, contattaci all\'indirizzo roma2lug@gmail.com\n'
		text += 'specificando il tuo ID  di registrazione: ' + assistance.participant.participant_id + '.\n\n'
	text += 'A presto,\nRoma2LUG e LugRoma3.\n'
	
	html = '<p>Caro ' + assistance.participant.first_name + ',<br />\n'
	html += 'ti informiamo che la tua richiesta di assistenza ha cambiato stato ed è stata <b>' + status + '</b>.<br />\n'
	if assistance.acceptance == Assistance.ACCEPTED:
		html += 'L\'appuntamento è stato fissato per le ' + assistance.accepted_time + '.<br />\n'
		html += 'Ricordati di presentare la tua email di registrazione all\'ingresso e di nuovo al banchetto assistenze.</p>\n'
	else:
		html += 'Per avere maggiori informazioni sul perché, contattaci all\'indirizzo roma2lug@gmail.com<br />\n'
		html += 'comunicando il tuo ID di registrazione: <b>' + assistance.participant.participant_id + '</b>.</p>\n'
	html += '<p>A presto,<br />Roma2LUG e LugRoma3.</p>\n'
	
	send_mail(subject, text, from_email, [to_email,], fail_silently=False, html_message=html)

# Send a generic email to participant(s)
def send_email(participants, subject, message):
	try:
		from_email = settings.EMAIL_CANONICAL_NAME + ' <' + settings.EMAIL_HOST_USER + '>'
	except AttributeError:
		from_email = settings.EMAIL_HOST_USER
	
	email_list = []
	for p in participants:
		email = str(p) + ' <' + p.email + '>'
		email_list.append((subject, message, from_email, [email,]))
	email_tuples = tuple(email_list)
	
	send_mass_mail(email_tuples, fail_silently=False)

# Given a search keyword(s) find all possible participants that match
def do_search(query):
	# Check if it is an ID
	if Participant.objects.filter(participant_id=query).exists():
		return Participant.objects.filter(participant_id=query)
	
	# Check if it is an email
	if '@' in query and Participant.objects.filter(email=query).exists():
		return Participant.objects.filter(email=query)
	
	p = []
	# Try the whole query as name
	p.extend(Participant.objects.filter(first_name__icontains=query)) # icontains: contains (substring) case insensitive
	p.extend(Participant.objects.filter(last_name__icontains=query))
	if len(p) > 0:
		return list(set(p)) # Get unique elements
	
	# No results yet: try splitting the query and check for name pieces
	substr = query.split()
	for s in substr:
		p.extend(Participant.objects.filter(first_name__icontains=s)) # icontains: contains (substring) case insensitive
		p.extend(Participant.objects.filter(last_name__icontains=s))
	
	return list(set(p)) # Get unique elements

PARTICIPATIONS = [
	[0, 'Mattina'],
	[1, 'Pomeriggio'],
	[2, 'Mattina e pomeriggio'],
]

# Registration form fields
class RegistrationForm(forms.Form):
	first_name = forms.CharField(label='Nome*', max_length=128, required=True)
	last_name = forms.CharField(label='Cognome*', max_length=128, required=True)
	email = forms.EmailField(label='Email*', required=True)
	participates = forms.ChoiceField(label='Partecipazione', choices=PARTICIPATIONS, required=False)
	comments = forms.CharField(label='Commenti', max_length=512, widget=forms.Textarea, required=False)
	mailing_list = forms.BooleanField(label='Consenti di ricevere email riguardanti il Linux Day come variazioni sul programma o eventi speciali.', initial=True, required=False)

# Registration form fields for administrators
class AdminRegistrationForm(forms.Form):
	first_name = forms.CharField(label='Nome*', max_length=128, required=True)
	last_name = forms.CharField(label='Cognome*', max_length=128, required=True)
	email = forms.EmailField(label='Email*', required=True)
	mailing_list = forms.BooleanField(label='Consenti di ricevere email riguardanti il Linux Day.', initial=True, required=False)

# Registration form fields for assistance requests
class AssistanceForm(forms.Form):
	email = forms.EmailField(label='Email*', help_text='Deve corrispondere a quella utilizzata in fase di registrazione.', required=True)
	pc_type = forms.ChoiceField(label='Tipo di computer*', choices=Assistance.PC_TYPES)
	brand = forms.CharField(label='Marca*', max_length=32, required=True)
	model = forms.CharField(label='Modello', max_length=32, required=False)
	cpu = forms.CharField(label='Processore', max_length=32, required=False)
	ram = forms.CharField(label='RAM', max_length=32, required=False)
	problem = forms.CharField(label='Problema*', widget=forms.Textarea, required=True)
	preferred_time = forms.TimeField(label='Orario preferito', help_text='Deve essere nella forma HH:mm. In base alla disponibilità dei nostri collaboratori potrebbe non essere rispettato. Fa fede l\'orario che comparirà nell\'email di conferma.', required=False)

# Basic objects that every template must have
def getBaseContext():
	context = {}
	
	# Check if public form is disabled
	if AdminProperty.objects.filter(key='disable_public_form', value='true').exists():
		context['public_form_disabled'] = True
	
	if AdminProperty.objects.filter(key='disable_assistances', value='true').exists():
		context['assistances_disabled'] = True
	
	return context

def changeProperties(request):
	# If requested to disable/enable the public form, change the object in the model
	disable_form = request.GET.get('disable_form')
	if disable_form:
		if disable_form == 'true':
			try:
				prop = AdminProperty.objects.get(key='disable_public_form')
				prop.value = 'true'
			except ObjectDoesNotExist:
				prop = AdminProperty(key='disable_public_form', value='true')
			prop.save()
		elif disable_form == 'false':
			try:
				prop = AdminProperty.objects.get(key='disable_public_form')
				prop.value = 'false'
			except ObjectDoesNotExist:
				prop = AdminProperty(key='disable_public_form', value='false')
			prop.save()
			
	# If requested to disable/enable the assistance form, change the object in the model
	disable_assistances = request.GET.get('disable_assistances')
	if disable_assistances:
		if disable_assistances == 'true':
			try:
				prop = AdminProperty.objects.get(key='disable_assistances')
				prop.value = 'true'
			except ObjectDoesNotExist:
				prop = AdminProperty(key='disable_assistances', value='true')
			prop.save()
		elif disable_assistances == 'false':
			try:
				prop = AdminProperty.objects.get(key='disable_assistances')
				prop.value = 'false'
			except ObjectDoesNotExist:
				prop = AdminProperty(key='disable_assistances', value='false')
			prop.save()

#####################################################################################################

# Views

@require_http_methods(['GET', 'POST'])
def index(request):
	if request.method == 'GET':
		if request.user.is_authenticated():
			# Enable / disable forms according to arguments of the GET request
			changeProperties(request)
			
			context = getBaseContext()
			
			# Populate the page summary
			registered_users = Participant.objects.count()
			context['registered_users'] = registered_users
			
			morning_users = Participant.objects.filter(participate_morning=True).count()
			context['morning_users'] = morning_users
			
			afternoon_users = Participant.objects.filter(participate_afternoon=True).count()
			context['afternoon_users'] = afternoon_users
			
			mailable_users = Participant.objects.filter(mailing_list=True).count()
			context['mailable_users'] = mailable_users
			
			seen_users = Participant.objects.filter(check_in__isnull=False).count()
			context['seen_users'] = seen_users
			
			pending_assistances = Assistance.objects.filter(acceptance__isnull=True).count()
			context['pending_assistances'] = pending_assistances
			
			accepted_assistances = Assistance.objects.filter(acceptance=Assistance.ACCEPTED).count()
			context['accepted_assistances'] = accepted_assistances
			
			not_accepted_assistances = Assistance.objects.filter(acceptance=Assistance.REFUSED).count()
			context['refused_assistances'] = not_accepted_assistances
			
			served_assistances = Assistance.objects.filter(operator__isnull=False).count()
			context['served_assistances'] = served_assistances
		
		else:
			# User is anonymous: show the public registration form
			form = RegistrationForm()
			context = getBaseContext()
			context['form'] = form
		
		return render(request, 'portal/index.html', context)
	
	# if this is a POST request we need to process the form data
	else:
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
				context = getBaseContext()
				context['form'] = form
				context['errors'] = True
				return render(request, 'portal/index.html', context)
			
			# Send the email
			if not DISABLE_EMAIL:
				t = threading.Thread(target=send_registration_email, args=(p,))
				t.start()
			else:
				print('Email disabled! No mail was sent to new registered user "' + form.cleaned_data['first_name'] + '".')
			
			# Populate the response
			reg_id = participant_id
			name = p.first_name
			return render(request, 'portal/result.html', {'reg_id': reg_id, 'name': name})
			
		else:
			# Invalid form, an error will be shown
			return render(request, 'portal/index.html', {'form': form})

@require_http_methods(['GET','POST'])
@login_required
def admin_form(request):
	# Registration form for logged in users
	
	if request.method == 'GET':
		# Show the registration form
		form = AdminRegistrationForm()
		return render(request, 'portal/admin_form.html', {'form': form})
	
	else:
		form = AdminRegistrationForm(request.POST)

		if form.is_valid():
			participant_id = getUniqueParticipantID()
			
			p = Participant(
							participant_id = participant_id,
							first_name = form.cleaned_data['first_name'],
							last_name = form.cleaned_data['last_name'],
							email = form.cleaned_data['email'],
							mailing_list = form.cleaned_data['mailing_list'],
							comments = 'Registrato durante l\'evento dall\'utente ' + str(request.user) + '.',
							participate_morning = True,
							participate_afternoon = True,
							check_in = datetime.now(),
			)
			try:
				p.save()
			except IntegrityError as e:
				context = getBaseContext()
				context['form'] = form
				context['error_message'] = 'L\'email usata sembra essere già presente nel sistema.'
				return render(request, 'portal/admin_form.html', context)
			
			# Send the email
			if not DISABLE_EMAIL:
				t = threading.Thread(target=send_registration_email, args=(p,))
				t.start()
			else:
				print('Email disabled! No mail was sent to new registered user "' + form.cleaned_data['first_name'] + '".')
			
			form = AdminRegistrationForm()
			context = getBaseContext()
			context['form'] = form
			context['confirm_message'] = 'Utente registrato con successo.'
			return render(request, 'portal/admin_form.html', context)
		else:
			context = getBaseContext()
			context['form'] = form
			return render(request, 'portal/admin_form.html', context)

# Participant views

@require_http_methods(['GET',])
@login_required
def participant_list(request):
	# List of all participants
	
	participants = Participant.objects.values(
			'participant_id',
			'last_name',
			'first_name',
			'participate_morning',
			'participate_afternoon',
			'registration_date',
			'mailing_list').order_by('last_name')
	
	context = getBaseContext()
	context['participants'] = participants
	context['message'] = 'Lista di tutte le persone iscritte'
	
	return render(request, 'portal/participant_list.html', context)

@require_http_methods(['GET',])
@login_required
def morning_users(request):
	# List of participants that should be present in the morning
	
	participants = Participant.objects.filter(participate_morning=True).values(
			'participant_id',
			'last_name',
			'first_name',
			'participate_morning',
			'participate_afternoon',
			'registration_date',
			'mailing_list').order_by('last_name')
	
	context = getBaseContext()
	context['participants'] = participants
	context['message'] = 'Lista degli iscritti per la mattina'
	
	return render(request, 'portal/participant_list.html', context)

@require_http_methods(['GET',])
@login_required
def afternoon_users(request):
	# List of participants that should be present in the afternoon
	
	participants = Participant.objects.filter(participate_afternoon=True).values(
			'participant_id',
			'last_name',
			'first_name',
			'participate_morning',
			'participate_afternoon',
			'registration_date',
			'mailing_list').order_by('last_name')
	
	context = getBaseContext()
	context['participants'] = participants
	context['message'] = 'Lista degli iscritti per il pomeriggio'
	
	return render(request, 'portal/participant_list.html', context)

@require_http_methods(['GET',])
@login_required
def mailing_list(request):
	# List of participants that allow to receive emails
	
	participants = Participant.objects.filter(mailing_list=True).values(
			'participant_id',
			'last_name',
			'first_name',
			'participate_morning',
			'participate_afternoon',
			'registration_date',
			'mailing_list').order_by('last_name')
	
	context = getBaseContext()
	context['participants'] = participants
	context['message'] = 'Lista delle persone autorizzate a ricevere email'
	
	return render(request, 'portal/participant_list.html', context)

@require_http_methods(['GET',])
@login_required
def checked_in(request):
	# List of participants already present at the event
	
	participants = Participant.objects.filter(check_in__isnull=False).values(
			'participant_id',
			'last_name',
			'first_name',
			'participate_morning',
			'participate_afternoon',
			'registration_date',
			'mailing_list').order_by('last_name')
	
	context = getBaseContext()
	context['participants'] = participants
	context['message'] = 'Persone già presenti all\'evento'
	
	return render(request, 'portal/participant_list.html', context)

@require_http_methods(['GET',])
@login_required
def participant_details(request, participant_id):
	participant = get_object_or_404(Participant, participant_id=participant_id)
	
	do_checkin = request.GET.get('do_checkin')
	if do_checkin:
		if do_checkin == 'true':
			participant.check_in = datetime.now()
		elif do_checkin == 'false':
			participant.check_in = None
		participant.save()
	
	context = getBaseContext()
	context['p'] = participant
	return render(request, 'portal/participant.html', context)

@require_http_methods(['GET',])
@login_required
def query_search(request):
	# Search form for participants
	
	participants = []
	
	query = request.GET.get('q')
	if query:
		participants = do_search(query)
	
	context = getBaseContext()
	context['participants'] = participants
	context['message'] = 'Risultati della ricerca'
	
	return render(request, 'portal/participant_list.html', context)

# Email management

@require_http_methods(['GET','POST'])
@login_required
def email_sender(request):
	if request.method == 'GET':
		participant_id = request.GET.get('id')
		if not participant_id:
			raise Http404('Non è stato richiesto nessun ID')
		if not (participant_id == 'all' or Participant.objects.filter(mailing_list=True, participant_id=participant_id).exists()):
			raise Http404('ID non valido')
		
		context = getBaseContext()
		context['participant_id'] = participant_id
		context['from'] = settings.EMAIL_CANONICAL_NAME + ' <' + settings.EMAIL_HOST_USER + '>'
		
		if participant_id == 'all':
			context['to'] = str(Participant.objects.filter(mailing_list=True).count()) + ' partecipanti'
		else:
			participant = Participant.objects.get(participant_id=participant_id)
			context['to'] = str(participant)
		
		return render(request, 'portal/emails.html', context)
	
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
		
		context = getBaseContext()
		context['confirm_message'] = 'L\'email è stata inviata a ' + str(len(participants)) + ' partecipanti.'
		return render(request, 'portal/emails.html', context)

# Assistance views

@require_http_methods(['GET','POST'])
def assistance_form(request):
	# Form for guest users
	
	if request.method == 'GET':
		form = AssistanceForm()
		
		context = getBaseContext()
		context['form'] = form
		
		return render(request, 'portal/assistance_form.html', context)
	
	else:
		form = AssistanceForm(request.POST)
		
		if form.is_valid():
			email = form.cleaned_data['email']
			try:
				p = Participant.objects.get(email=email)
			except ObjectDoesNotExist:
				context = getBaseContext()
				context['form'] = form
				context['error_message'] = 'L\'indirizzo email non è stato trovato nel sistema, devi prima iscriverti all\'evento'
				return render(request, 'portal/assistance_form.html', context)
			if Assistance.objects.filter(participant=p).exists():
				context = getBaseContext()
				context['form'] = form
				context['error_message'] = 'Hai già fatto una richiesta di assistenza. Per eventuali problemi contattaci all\'indirizzo roma2lug@gmail.com'
				return render(request, 'portal/assistance_form.html', context)
			
			a = Assistance(
					participant = p,
					pc_type = form.cleaned_data['pc_type'],
					brand = form.cleaned_data['brand'],
					model = form.cleaned_data['model'],
					cpu = form.cleaned_data['cpu'],
					ram = form.cleaned_data['ram'],
					problem = form.cleaned_data['problem'],
					preferred_time = form.cleaned_data['preferred_time'],
			)
			try:
				a.save()
			except IntegrityError as e:
				context = getBaseContext()
				context['form'] = form
				context['error_message'] = 'Si è verificato un errore nella richiesta, riprova o contattaci all\'indirizzo roma2lug@gmail.com'
				return render(request, 'portal/assistance_form.html', context)
			
			context = getBaseContext()
			context['form'] = form
			context['confirm_message'] = 'La richiesta è stata inoltrata con successo. Riceverai un\'email di conferma quando verrà visionata dai nostri membri.'
			return render(request, 'portal/assistance_form.html', context)
			
		else:
			context = getBaseContext()
			context['form'] = form
			return render(request, 'portal/assistance_form.html', context)

@require_http_methods(['GET',])
@login_required
def assistance_list(request):
	# All assistances
	
	assistances = Assistance.objects.values(
			'participant__participant_id',
			'participant__last_name',
			'participant__first_name',
			'pc_type',
			'acceptance',
			'accepted_time',
			'estimated_mttr').order_by('participant__last_name',)
	
	context = getBaseContext()
	context['assistances'] = assistances
	context['message'] = 'Lista di tutte le richieste di assistenza'
	
	# Filters are defined in templatetags/portal_filters.py
	return render(request, 'portal/assistance_list.html', context)

@require_http_methods(['GET',])
@login_required
def pending_assistances(request):
	# Pending assistances
	
	assistances = Assistance.objects.filter(acceptance__isnull=True).values(
			'participant__participant_id',
			'participant__last_name',
			'participant__first_name',
			'pc_type',
			'acceptance',
			'accepted_time',
			'estimated_mttr').order_by('participant__last_name',)
	
	context = getBaseContext()
	context['assistances'] = assistances
	context['message'] = 'Lista delle richieste di assistenza pendenti'
	
	# Filters are defined in templatetags/portal_filters.py
	return render(request, 'portal/assistance_list.html', context)

@require_http_methods(['GET',])
@login_required
def accepted_assistances(request):
	# Accepted assistances
	
	assistances = Assistance.objects.filter(acceptance=Assistance.ACCEPTED).values(
			'participant__participant_id',
			'participant__last_name',
			'participant__first_name',
			'pc_type',
			'acceptance',
			'accepted_time',
			'estimated_mttr').order_by('participant__last_name',)
	
	context = getBaseContext()
	context['assistances'] = assistances
	context['message'] = 'Lista delle richieste di assistenza accettate'
	
	# Filters are defined in templatetags/portal_filters.py
	return render(request, 'portal/assistance_list.html', context)

@require_http_methods(['GET',])
@login_required
def refused_assistances(request):
	# Refused assistances
	
	assistances = Assistance.objects.filter(acceptance=Assistance.REFUSED).values(
			'participant__participant_id',
			'participant__last_name',
			'participant__first_name',
			'pc_type',
			'acceptance',
			'accepted_time',
			'estimated_mttr').order_by('participant__last_name',)
	
	context = getBaseContext()
	context['assistances'] = assistances
	context['message'] = 'Lista delle richieste di assistenza rifiutate'
	
	# Filters are defined in templatetags/portal_filters.py
	return render(request, 'portal/assistance_list.html', context)

@require_http_methods(['GET',])
@login_required
def served_assistances(request):
	# Refused assistances
	
	assistances = Assistance.objects.filter(operator__isnull=False).values(
			'participant__participant_id',
			'participant__last_name',
			'participant__first_name',
			'pc_type',
			'acceptance',
			'accepted_time',
			'estimated_mttr').order_by('participant__last_name',)
	
	context = getBaseContext()
	context['assistances'] = assistances
	context['message'] = 'Lista delle richieste di assistenza già servite'
	
	# Filters are defined in templatetags/portal_filters.py
	return render(request, 'portal/assistance_list.html', context)

@require_http_methods(['GET'])
@login_required
def assistance_details(request, participant_id):
	assistance = get_object_or_404(Assistance, participant__participant_id=participant_id)
	
	if request.method == 'GET':
		get_assistance = request.GET.get('get_assistance')
		if get_assistance:
			if get_assistance == 'true' and assistance.operator == None:
				assistance.operator = request.user
			elif get_assistance == 'false' and assistance.operator == request.user:
				assistance.operator = None
			assistance.save()
		
		context = getBaseContext()
		context['assistance'] = assistance
		return render(request, 'portal/assistance.html', context)

@require_http_methods(['GET','POST'])
@login_required
def assistance_status(request, participant_id):
	assistance = get_object_or_404(Assistance, participant__participant_id=participant_id)
	
	if request.method == 'GET':
		context = getBaseContext()
		context['assistance'] = assistance
		return render(request, 'portal/assistance_status.html', context)
	
	else:
		status = request.POST['status']
		accepted_time = request.POST['accepted_time']
		estimated_mttr = request.POST['estimated_mttr']
		
		# If status == ACCEPTED other fields must be filled in
		if status == Assistance.ACCEPTED and (not accepted_time or not estimated_mttr):
			context = getBaseContext()
			context['assistance'] = assistance
			context['error_message'] = 'Se si accetta l\'assistenza occorre specificare un orario e un tempo stimato di intervento.'
			return render(request, 'portal/assistance_status.html', context)
		
		# Required to determine if we must send the email or not
		old_status = assistance.acceptance
		
		# Update fields and save the object
		assistance.acceptance = status
		if status == Assistance.ACCEPTED:
			assistance.accepted_time = accepted_time
			assistance.estimated_mttr = estimated_mttr
		elif status == Assistance.REFUSED:
			assistance.accepted_time = None
			assistance.estimated_mttr = None
		else:
			context = getBaseContext()
			context['assistance'] = assistance
			context['error_message'] = 'Occorre specificare uno stato valido.'
			return render(request, 'portal/assistance_status.html', context)
		try:
			assistance.save()
		except IntegrityError as e:
			context = getBaseContext()
			context['assistance'] = assistance
			context['error_message'] = 'Si è verificato un errore nella richiesta, controlla che i campi siano validi.'
			return render(request, 'portal/assistance_status.html', context)
		
		# Send the email if status changed
		if old_status != status:
			if not DISABLE_EMAIL:
				t = threading.Thread(target=send_assistance_email, args=(assistance,))
				t.start()
			else:
				print('Email disabled! No email was sent to "' + str(assistance.participant) + '" for changes in assistance status.')
		
		assistance = Assistance.objects.get(participant__participant_id=participant_id)
		context = getBaseContext()
		context['assistance'] = assistance
		context['confirm_message'] = 'Le modifiche sono state salvate'
		return render(request, 'portal/assistance_status.html', context)

#####################################################################################################

# REST Interfaces
class RESTParticipantList(generics.ListAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	queryset = Participant.objects.all()
	serializer_class = ParticipantSerializer

class RESTParticipantDetails(generics.RetrieveUpdateAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	queryset = Participant.objects.all()
	serializer_class = ParticipantSerializer

class RESTAssistanceList(generics.ListAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	queryset = Assistance.objects.all()
	serializer_class = AssistanceSerializer

class RESTAssistanceDetails(generics.RetrieveUpdateAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	queryset = Assistance.objects.all()
	serializer_class = AssistanceSerializer

#####################################################################################################

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
			context = {
						'error_message': 'Errore di autenticazione!',
						'username': username
			}
			return render(request, 'portal/login.html', context)

def logout(request):
	if request.user.is_authenticated():
		django.contrib.auth.logout(request)
		
	return render(request, 'portal/logout.html')

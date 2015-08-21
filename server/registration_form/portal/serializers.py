# ----------------------------------------------------------------------- #
# Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                         #
# ----------------------------------------------------------------------- #

from rest_framework import serializers
from portal.models import Participant, Assistance

from django.contrib.auth import get_user_model

class ParticipantSerializer(serializers.ModelSerializer):
	class Meta:
		model = Participant
		fields = ('participant_id', 'first_name', 'last_name', 'email', 'participate_morning', 'participate_afternoon', 'registration_date', 'check_in', 'comments')
		read_only_fields = ('participant_id', 'first_name', 'last_name', 'email', 'participate_morning', 'participate_afternoon', 'registration_date', 'comments')

class AssistanceSerializer(serializers.ModelSerializer):
	participant = serializers.SlugRelatedField(read_only=True, slug_field='participant_id')
	operator = serializers.SlugRelatedField(read_only=False, allow_null=True, slug_field='username', queryset=get_user_model().objects.all())
	
	class Meta:
		model = Assistance
		fields = ('participant', 'pc_type', 'brand', 'model', 'cpu', 'ram', 'problem', 'acceptance', 'accepted_time', 'estimated_mttr', 'operator')
		read_only_fields = ('pc_type', 'brand', 'model', 'cpu', 'ram', 'problem', 'acceptance', 'accepted_time', 'estimated_mttr')

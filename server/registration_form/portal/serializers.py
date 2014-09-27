from rest_framework import serializers
from portal.models import Participant

class ParticipantSerializer(serializers.ModelSerializer):
	class Meta:
		model = Participant
		fields = ('id', 'first_name', 'last_name', 'email', 'participate_morning', 'participate_afternoon', 'registration_date', 'check_in', 'comments')
		read_only_fields = ('registration_date',)

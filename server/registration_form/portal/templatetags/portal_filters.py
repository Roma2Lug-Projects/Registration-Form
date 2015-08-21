# ----------------------------------------------------------------------- #
# Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                         #
# ----------------------------------------------------------------------- #

from portal.models import Assistance
from django import template

register = template.Library()

@register.filter
def pc_type(typez):
	for t in Assistance.PC_TYPES:
		if t[0] == typez:
			return t[1]
	return ''

@register.filter
def acceptance_status(status):
	for s in Assistance.STATUS:
		if s[0] == status:
			return s[1]
	return 'Pendente'

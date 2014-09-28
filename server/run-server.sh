#!/bin/bash

# ------------------------------------------------------------------- #
# Copyright (C) 2014 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                     #
# ------------------------------------------------------------------- #

ADDRESS="0.0.0.0"
PORT="8000"

source ./environment 2>/dev/null
if [ $? != "0" ] ; then
	echo -e "Cannot import environment path" >&2
	exit 1
fi

source $VIRT_ENV/bin/activate
if [ $? != "0" ] ; then
	echo -e "Cannot access virtual environment" >&2
	exit 1
fi

python $DJANGO_PROJ/manage.py runserver $ADDRESS:$PORT

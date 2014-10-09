#!/bin/bash

# ------------------------------------------------------------------- #
# Copyright (C) 2014 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                     #
# ------------------------------------------------------------------- #

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $DIR/environment 2>/dev/null
if [ $? != "0" ] ; then
	echo -e "Cannot import environment path" >&2
	exit 1
fi

source $VIRT_ENV/bin/activate
if [ $? != "0" ] ; then
	echo -e "Cannot access virtual environment" >&2
	exit 1
fi

echo "Creating superuser..."
python $DJANGO_PROJ/manage.py createsuperuser
if [ $? != "0" ] ; then
	echo -e "Error creating superuser" >&2
	exit 1
fi

echo "DONE!"
exit 0

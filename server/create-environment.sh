#!/bin/bash

# ----------------------------------------------------------------------- #
# Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                         #
# ----------------------------------------------------------------------- #

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $DIR/environment 2> /dev/null
if [ $? != "0" ] ; then
	echo -e "Cannot import environment path" >&2
	exit 1
fi



##########################
# Checking configuration #
##########################

echo -e "Checking configuration...\n" >&2

echo -n "Checking python3... "
if [ ! `command -v python3 2> /dev/null` ] ; then
	echo -e "FAILED!\n\nPlease install python3 and retry."
	exit 1
fi
echo "OK!"

echo -n "Checking virtualenv... "
if [ ! `command -v virtualenv 2> /dev/null` ] ; then
	echo -e "FAILED!\n\nPlease install virtualenv and retry."
	exit 1
fi
echo "OK!"

echo -n "Checking environment path... "
if [[ $VIRT_ENV =~ ^.*[[:space:]].*$ ]] ; then
	echo -e "FAILED!\n\nENVIRONMENT path must not contain spaces" >&2
	exit 1
fi
echo "OK!"



echo -ne "\nInstalling virtual environment... "

if [ `virtualenv -p python3 $VIRT_ENV > /dev/null` ] ; then
	echo -e "FAILED!\n\nCannot install virtual environment.\nIs the directory writable?" >&2
	exit 1
fi
echo "OK!"



source $VIRT_ENV/bin/activate
if [ $? != "0" ] ; then
	echo -e "Cannot access virtual environment" >&2
	exit 1
fi



#######################
# Installing packages #
#######################

# Requirements for Django-norel
echo -ne "Installing Django... "
pip3 install Django > /dev/null
if [ $? != "0" ] ; then
	echo -e "FAILED!\n\nCannot install Django." >&2
	exit 1
fi
echo "OK!"

# Requirements for Django REST framework
echo -ne "Installing Django REST framework."
pip3 install djangorestframework > /dev/null
if [ $? != "0" ] ; then
	echo -e "FAILED!\n\nCannot install Django REST framework." >&2
	exit 1
fi
echo -n "."
pip3 install markdown > /dev/null       # Markdown support for the browsable API.
if [ $? != "0" ] ; then
	echo -e "FAILED!\n\nCannot install Django REST framework." >&2
	exit 1
fi
echo -n ". "
pip3 install django-filter > /dev/null  # Filtering support
if [ $? != "0" ] ; then
	echo -e "FAILED!\n\nCannot install Django REST framework." >&2
	exit 1
fi
echo "OK!"

# Requirements for QRCode
echo -ne "Installing QRCode"
pip3 install qrcode > /dev/null
if [ $? != "0" ] ; then
	echo -e "FAILED!\n\nCannot install QRCode." >&2
	exit 1
fi
echo -n "."
pip3 install pillow > /dev/null
if [ $? != "0" ] ; then
	echo -e "FAILED!\n\nCannot install Pillow. You need python3-dev and python3-setuptools packages." >&2
	exit 1
fi
echo -n "."
pip3 install https://github.com/ojii/pymaging/archive/master.zip > /dev/null
if [ $? != "0" ] ; then
	echo -e "FAILED!\n\nCannot install pymaging." >&2
	exit 1
fi
echo -n ". "
pip3 install https://github.com/ojii/pymaging-png/archive/master.zip > /dev/null
if [ $? != "0" ] ; then
	echo -e "FAILED!\n\nCannot install pymaging-png." >&2
	exit 1
fi
echo "OK!"



#####################
# Setting up Django #
#####################

echo -e "\nSetting up Django..."
python3 $DJANGO_PROJ/manage.py migrate > /dev/null
if [ $? != "0" ] ; then
	echo -e "Error synchronizing database. Check manually" >&2
	exit 1
fi

read -p "Do you want to create a new superuser [Y|n]? " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]
then
	echo "You can always create a superuser using script create-superuser.sh"
else
	echo "Creating superuser..."
	python3 $DJANGO_PROJ/manage.py createsuperuser
	if [ $? != "0" ] ; then
		echo -e "Error creating superuser" >&2
		exit 1
	fi
fi

echo -e "\nEND"

exit 0

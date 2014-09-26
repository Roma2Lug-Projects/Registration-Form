#!/bin/bash

source ./environment 2>/dev/null
if [ $? != "0" ] ; then
	echo -e "Cannot import environment path" >&2
	exit 1
fi



##########################
# Checking configuration #
##########################

echo -e "Checking configuration...\n" >&2

echo -n "Checking python2.7... "
if [ ! `command -v python2.7 2>/dev/null` ] ; then
	echo -e "FAILED!\n\nPlease install python2.7 and retry."
	exit 1
fi
echo "OK!"

echo -n "Checking virtualenv... "
if [ ! `command -v virtualenv 2>/dev/null` ] ; then
	echo -e "FAILED!\n\nPlease install virtualenv and retry."
	exit 1
fi
echo "OK!"

echo -n "Checking pip... "
if [ ! `command -v pip 2>/dev/null` ] ; then
	echo -e "FAILED!\n\nPlease install pip and retry."
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

if [ `virtualenv $VIRT_ENV >/dev/null` ] ; then
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
pip install Django >/dev/null
if [ $? != "0" ] ; then
	echo -e "FAILED!\n\nCannot install Django." >&2
	exit 1
fi
echo "OK!"

# Requirements for Django REST framework
echo -ne "Installing Django REST framework."
pip install djangorestframework >/dev/null
if [ $? != "0" ] ; then
	echo -e "FAILED!\n\nCannot install Django REST framework." >&2
	exit 1
fi
echo -n "."
pip install markdown >/dev/null       # Markdown support for the browsable API.
if [ $? != "0" ] ; then
	echo -e "FAILED!\n\nCannot install Django REST framework." >&2
	exit 1
fi
echo -n ". "
pip install django-filter >/dev/null  # Filtering support
if [ $? != "0" ] ; then
	echo -e "FAILED!\n\nCannot install Django REST framework." >&2
	exit 1
fi
echo "OK!"

# Requirements for QRCode
echo -ne "Installing QRCode... "
pip install qrcode >/dev/null
if [ $? != "0" ] ; then
	echo -e "FAILED!\n\nCannot install QRCode." >&2
	exit 1
fi
echo "OK!"



#####################
# Setting up Django #
#####################

echo -e "\nSetting up Django..."
python $DJANGO_PROJ/manage.py migrate >/dev/null
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
	python $DJANGO_PROJ/manage.py createsuperuser
	if [ $? != "0" ] ; then
		echo -e "Error creating superuser" >&2
		exit 1
	fi
fi

echo -e "\nEND"

exit 0

# Linux Day Registration Form

---------------------------------------------------------------------

Copyright (C) 2014-2015 Federico "MrModd" Cosentino (http://mrmodd.it/)
on behalf of Roma2LUG (http://lug.uniroma2.it/)

Django-bootstrap-form Copyright (c) by Ming Hsien Tzang
Bootstrap under MIT license

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

---------------------------------------------------------------------

## What is it?

This project is the registration form for the Linux Day 2015 event organized
by Roma2LUG and LUGRoma3. It is divided in a server and a client:

- **server**: this part is a Web server, written in Python with the Django
  framework and the Django-REST-framework interface. Users which want to
  participate at the event, access the main page of this server and compile
  the form. At the end, an email is sent to them with their unique ID and
  a QR Code that will be used the day of the event to register the presence.

- **client**: this is an Android application that should be used by the event
  staff at the acceptance. When a participant arrives, he shows the QR Code
  he recived by email; a staff member scans the code with this app and retrieve
  all the user's information from the server. Then presses Record button to
  Save in the system the time the participant arrived.

## Server

There are some things you should know before run the server:

### Available URLs

If the server URL is http://example.com:8080/, these URLs are available:

- *http://example.com:8080/*: this is the index of the portal and can be accessed
  from the browser;
- *http://example.com:8080/admin/*: this is the Django administration portal
  where you can create and delete administration users and manage objects
  in the database
- *http://example.com:8080/qr/<id>*: where id is an alphanumerical code
  of 16 digits, this page shows a QR Code with the given ID as text
- *http://example.com:8080/qr/<id>.svg*: this page generate an svg image of
  a QR Code with the given ID written in it
- *http://example.com:8080/qr/<id>.png*: same as above, but in png format

The following REST interfaces are available:

- *http://example.com:8080/rest/participants/*: lists all participants
- *http://example.com:8080/rest/participants/<id>/*: where id is an alphanumerical code
  of 16 digits, this interface shows the participant details
- *http://example.com:8080/rest/assistances/*: lists all assistances
- *http://example.com:8080/rest/assistances/<id>/*: where id is an alphanumerical code
  of 16 digits, this interface shows the details of an assistance

### Important files

- *server/environment*: this file contains some variables such as the virtual
  environment installation folder and the Django project folder
- *server/create-environment.sh*: this script setup the Django environment;
  it checks for prerequisites, performs the virtual environment installation
  and runs the server for the first time
- *server/create-superuser.sh*: previous script should ask for the superuser
  creation, but if you skipped that phase you can use this to create a new one
- *server/run-server.sh*: this runs the server. You should have performed the
  environment creation first
- *server/clean-server.sh*: this destroys every user file, including the server
  database and the Django secret key
- *server/registration_form/db.sqlite3*: this is the server database
- *server/registration_form/secret_key.txt*: this is the Django server key, you
  should keep this file safe. It is automatically generated if absent
- *server/registration_form/registration_form/local_settings.py*: this file contains
  SMTP server credentials, used to send emails. This is not present by default, you
  should copy the local_settings.py.example and edit the required fields

### Installation guide with Apache

- You need to install Apache server (but not an entire LAMP server). On Ubuntu or Debian
  install apache2 and libapache2-mod-wsgi-py3:

		~# apt-get install apache2 libapache2-mod-wsgi-py3

- Now you need Python virtualenv:

		~# apt-get install python-virtualenv

- Some Python packages also require python3-dev, python3-setuptools and gcc:

		~# apt-get install python3-dev python3-setuptools build-essential

- Move *server/registration_form/registration_form/local_settings.py.example* in
  *server/registration_form/registration_form/local_settings.py*:

		~$ mv server/registration_form/registration_form/local_settings.py.example\
		 > server/registration_form/registration_form/local_settings.py

- Modify this file with your data. Next steps assume you DIDN'T modify *STATIC_ROOT* and
  *STATIC_URL* variables

- Copy *server/registration_form* in */var/www/*:

		~# cp -r server/registration_form /var/www

- Edit file *server/environment* and change *SERV_PATH* from *"."* to *"/var/www"*
- Build virtual environment executing script *server/create-environment.sh*, afterward you
  should see a new *virtual* folder in */var/www/*:

		~# server/create-environment.sh

- Create a new folder in */var/www/* called *static*:

		~# mkdir /var/www/static

- Populate the static folder with files collected from Django. Use
  *server/update-static.sh* script to do the magic:

		~# server/update-static.sh

- Keep in mind these paths you should have:
- - */var/www/static/*
- - */var/www/registration_form/registration_form/wsgi.py*
- - */var/www/virtual/lib/python3.4/site-packages/*

- Now you need to edit Apache sites configuration file:
- - Copy the config file from server folder into Apache:

		~# cp server/apache-django.conf /etc/apache2/sites-available/

- - Remember to change */var/www/static* path if you changed it in *local_settings.py* file
- - Enable SSL module:

		~# a2enmod ssl

- - Disable default configurations and enable the correct one:

		~# a2dissite 000-default.conf
		~# a2dissite default-ssl.conf
		~# a2ensite apache-django.conf

- Finally give correct permissions to the folder:

		~# chown -R www-data:www-data /var/www/

- And restart the server:

		~# service apache2 restart

- Now you should navigate typing http://localhost/ or https://localhost/

- Optionally change the Apache default self-signed certificates with new ones:

		~# openssl req -new -x509 -days 365 -nodes -out /etc/ssl/certs/apache-django.pem -keyout /etc/ssl/private/apache-django.key

  and then change the paths of these files in */etc/apache2/sites-available/apache-django.conf* file you previously
  copied. In particular change **SSLCertificateFile** and **SSLCertificateKeyFile** directives.

## Client

*client* folder is an Eclipse project. It is compiled for Android SDK version from 14
up to 21. It uses the basic authentication method to connect to the REST interface
of the server. You can configure URL, username and password from the preference menu.
Username and password are those set during the environment creation. You can create
a new user with *create-superuser.sh* script. URL should be something like
http://example.com:8080/rest/ and should end with /. Remember to put the base URL for
the REST interface and not the server URL (in a few words remember to end the URL with
rest/).
You need to have the QR Code scanner on the phone, otherwise this app will prompt you
to install it.
You can fetch a participant details scanning its QR Code or typing his ID manually.
When you can see his details on the app you can proceed to check in his presence.


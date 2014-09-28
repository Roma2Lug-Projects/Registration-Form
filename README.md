# Linux Day Registration Form

---------------------------------------------------------------------

Copyright (C) 2014 Federico "MrModd" Cosentino (http://mrmodd.it/)
on behalf of Roma2LUG (http://lug.uniroma2.it/)

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

This project is the registration form for the Linux Day 2014 event organized
by Roma2LUG. It is divided in a server and a client:

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

- *http://example.com:8080/*: this is the registration form where the users
  sign for their presence at the event
- *http://example.com:8080/rest/*: this is the base URL for the REST interface,
  it is also available from browser
- *http://example.com:8080/rest/1/*: where 1 is an ID (it can be any integer number),
  this URL is the REST interface for the details of the user with this ID
- *http://example.com:8080/admin/*: this is the Django administration portal
  where you can create and delete administration users and manage participant
  registrations
- *http://example.com:8080/qr/123*: this page shows a QR Code with ID 123
- *http://example.com:8080/qr/dl/123.svg*: this page generate an svg image of
  a QR Code with 123 written in it
- *http://example.com:8080/qr/dl/123.png*: same as above, but in png format

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
When you can see his details on the app you can procede to check in his presence.

#!/bin/bash

read -p "Are you sure you want to clean the server installation? This will erase all data! [y|N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
	rm -rf virtual/
	rm -rf registration_form/db.sqlite3
	find ./registration_form -name "*.pyc" -exec rm -rf {} \;
else
	echo "Aborted."
fi

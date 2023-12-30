#!/usr/bin/bash
if [ "$SNAP" == "" ]
then
	python3 /app/app_window.py
else
	python3 $SNAP/usr/app_window.py
fi

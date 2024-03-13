#!/bin/bash
#source env/bin/activate &&
#python manage.py migrate
cd /scuba/apps/scubamob && python3 -m venv env && . env/bin/activate && python3 manage.py migrate

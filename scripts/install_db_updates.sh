#!/bin/bash
#source env/bin/activate &&
#python manage.py migrate
cd /scuba/apps/scubamob && . env/bin/activate && python3 manage.py migrate

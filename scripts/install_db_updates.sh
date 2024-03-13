#!/bin/bash
cd /scuba/apps
python3 -m venv env
. env/bin/activate
cd /scuba/apps/scubamob
pip install -r requirements.txt
python3 manage.py migrate

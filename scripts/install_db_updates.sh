#!/bin/bash
cd /scuba
python3 -m venv env
source env/bin/activate
cd /scuba/apps/scubamob
pip install -r requirements.txt
python3 manage.py migrate

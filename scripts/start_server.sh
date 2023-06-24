#!/bin/bash
source /scuba/apps/env/bin/activate && pip install -r requirements.txt
source /scuba/apps/env/bin/activate && cd /scuba/apps/scubamob && python manage.py migrate
service nginx start

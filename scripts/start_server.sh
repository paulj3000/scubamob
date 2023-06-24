#!/bin/bash
#source /scuba/apps/env/bin/activate && cd /scuba/apps/scubamob && pip install -r requirements.txt
#source /scuba/apps/env/bin/activate && cd /scuba/apps/scubamob && python manage.py migrate
service nginx restart
service scuba restart

#!/bin/bash
source /scuba/apps/env/bin/activate && cd /scuba/apps/scubamob && pip install -r requirements.txt
source /scuba/apps/env/bin/activate && cd /scuba/apps/scubamob && python manage.py migrate
source /scuba/apps/env/bin/activate && cd /scuba/apps/scubamob && python manage.py collectstatic --noinput
chmod -R 775 /scuba/apps/scubamob
chown -R ubuntu:ubuntu /scuba/apps/scubamob
service nginx restart
service scuba restart

#!/bin/bash
. /scuba/apps/env/bin/activate
cd /scuba/apps/scubamob
python3 manage.py collectstatic -l --noinput

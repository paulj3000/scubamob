#!/bin/bash
cd ../../ && 
    npm install &&
    npm run build &&
    source env/bin/activate &&
    python manage.py compress --force &&
    python manage.py collectstatic --no-input &&
    pip install -r requirements.txt

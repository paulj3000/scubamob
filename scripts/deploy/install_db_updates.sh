#!/bin/bash
cd ../../ && 
    source env/bin/activate &&
    python manage.py makemigrations

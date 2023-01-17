#!/bin/sh

if [ "$DATABASE" = "mysql" ]
then
    echo "Waiting for mysql..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "MySQL started"
fi

source ./env/bin/activate
python manage.py flush --no-input
python manage.py migrate
python manage.py loaddata scuba/home/fixtures/home.json scuba/sitesettings/fixtures/site_settings.json scuba/accounts/fixtures/firstuser.json

exec "$@"

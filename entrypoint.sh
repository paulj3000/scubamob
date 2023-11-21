#!/bin/sh

python3 -m venv /scuba/app/scubamob/./env
#source ./env/bin/activate
source /scuba/app/scubamob/./env/bin/activate
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir -r requirements.txt
pip install mysqlclient==2.1.0
python manage.py flush --no-input
python manage.py migrate

npm install
npm run build
python manage.py compress --force
python manage.py collectstatic --noinput

if [ "$DATABASE" = "mysql" ]
then
    echo "Waiting for mysql..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "MySQL started"
fi

python manage.py loaddata scuba/home/fixtures/home.json scuba/sitesettings/fixtures/site_settings.json scuba/accounts/fixtures/firstuser.json

exec "$@"

#!/bin/sh

if [ "$DATABASE" = "mysql" ]
then
    echo "Waiting for mysql..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "MySQL started"
fi

pip install --upgrade pip
pip install -r requirements.txt
npm install
npm run build

python manage.py flush --no-input
python manage.py makemigrations accounts sitesettings home galleries
python manage.py migrate
python manage.py compress --force
python manage.py collectstatic --noinput
python manage.py loaddata scuba/home/fixtures/home.json scuba/sitesettings/fixtures/site_settings.json scuba/accounts/fixtures/firstuser.json

rm gulpfile.js
rm webpack.config.js
rm .babelrc

exec "$@"

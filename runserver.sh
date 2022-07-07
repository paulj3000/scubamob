#!/bin/bash

if [[ -z $(docker ps | grep "mongo" | awk '{ print $1 }')  ]]; then
docker run -it -d -p 27017:27017 mongo
fi

if [[ -z $(docker ps | grep "memcached" | awk '{ print $1 }')  ]]; then
docker run -it -d -p 11211:11211 memcached
fi

python manage.py runserver 0.0.0.0:8002

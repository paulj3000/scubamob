#!/bin/bash

if [[ -z $(docker ps | grep "memcached" | awk '{ print $1 }')  ]]; then
docker run -it -d -p 11211:11211 memcached
fi

python3 manage.py runserver 0.0.0.0:8002

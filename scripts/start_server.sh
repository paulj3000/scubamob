#!/bin/bash

if [ ! -f /etc/systemd/system/scuba.service ]; then
    aws s3 cp s3://scubamob-deploy/scripts/${DEPLOYMENT_GROUP_NAME}/scuba.service /etc/systemd/system/scuba.service
    systemctl enable scuba
fi

if [ ! -f /etc/nginx/sites-enabled/scubamob.conf ]; then
    aws s3 cp s3://scubamob-deploy/scripts/${DEPLOYMENT_GROUP_NAME}/scubamob.conf /etc/nginx/sites-enabled/scubamob.conf
fi

chown -R ubuntu:ubuntu /scuba/apps/scubamob
service nginx restart
service scuba restart

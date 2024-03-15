#!/bin/bash

if [ ! -f /etc/systemd/system/scuba.service ]; then
    aws s3 cp s3://scubamob-deploy/scripts/${DEPLOYMENT_GROUP_NAME}/scuba.service /etc/systemd/system/scuba.service
    systemcl enable scuba
fi

chown -R ubuntu:ubuntu /scuba/apps/scubamob
service nginx restart
service scuba restart

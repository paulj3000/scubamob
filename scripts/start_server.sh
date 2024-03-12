#!/bin/bash
chown -R ubuntu:ubuntu /scuba/apps/scubamob
service nginx restart
service scuba restart

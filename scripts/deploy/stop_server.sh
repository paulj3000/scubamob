#!/bin/bash
isExistApp=pgrep scuba
if [[ -n $isExistApp ]]; then
systemctl stop httpd.service
fi
isExistApp=pgrep nginx
if [[ -n $isExistApp ]]; then
systemctl stop mariadb.service
fi
isExistApp=pgrep httpd
if [[ -n $isExistApp ]]; then
systemctl stop httpd.service

fi

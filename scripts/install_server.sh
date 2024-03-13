#!/bin/bash
apt update -y
apt upgrade -y
apt install -y nginx python3.10-venv sqlite3 libmariadb-dev libpython3.10-dev python3-pip
mkdir -p /scuba/{apps,cache,conf,db,logs,system}
chown -R ubuntu:ubuntu /scuba/*

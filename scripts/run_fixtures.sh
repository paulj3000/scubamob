#!/bin/bash
find ../scuba -wholename '*/fixtures/*' | xargs python ../manage.py

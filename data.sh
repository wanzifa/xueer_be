#!/usr/bin/env bash
# !/bin/sh

# create migrate floder
python manage.py db init

# first migrate
python manage.py db migrate -m "init migrate"

# database upgrade
python manage.py db upgrade

# create user Roles
python manage.py shell

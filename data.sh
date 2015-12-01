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

# adduser
echo "add user neo1218"
echo "please input password and confirm the password"
python manage.py adduser neo1218 neo1218@yeah.net

# done!
echo "\n"
echo "----------------------------------"
echo "create test database done!"
echo "test database: xueer_dev.sqlite"
echo "test user: neo1218"
echo "test user email: neo1218@yeah.net"
echo "fake data: count = 100"
echo "----------------------------------"

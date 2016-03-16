# /bin/sh

# start xueer
echo "start xueer!"
sudo ./venv/bin/uwsgi --ini xueer.ini&

echo "start nginx!"
sudo systemctl start nginx

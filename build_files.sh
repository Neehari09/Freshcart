#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py loaddata store_fixture.json
python manage.py collectstatic --noinput

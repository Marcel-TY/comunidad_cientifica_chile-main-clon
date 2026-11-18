#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
npm ci --prefix frontend
npm run build --prefix frontend
python comunidad_cientifica/manage.py collectstatic --noinput

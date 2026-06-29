#!/bin/bash
set -e

cd /home/hbc3869/copd-prediction
source .venv/bin/activate

git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

sudo systemctl restart gunicorn.service

echo "배포 완료: $(date)"

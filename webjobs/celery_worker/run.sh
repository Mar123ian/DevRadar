#!/bin/bash

echo "Starting Celery Worker..."

cd /home/site/wwwroot

celery -A devradar worker --loglevel=info
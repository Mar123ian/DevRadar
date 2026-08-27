#!/bin/sh

# Стартираме Celery с Eventlet във фонов режим
celery -A devradar worker --loglevel=info -P eventlet &

# Стартираме Daphne уеб сървъра на преден план
daphne -b 0.0.0.0 -p 8000 devradar.asgi:application
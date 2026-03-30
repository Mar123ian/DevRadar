#!/bin/bash
echo "Starting Celery Worker..."

PROJECT_DIR=$(find /tmp -maxdepth 1 -type d -exec test -f "{}/manage.py" \; -print | head -n 1)

if [ -z "$PROJECT_DIR" ]; then
    echo "ERROR: Project folder not found in /tmp!"
    exit 1
fi

echo "Project folder detected: $PROJECT_DIR"

VENV_DIR="$PROJECT_DIR/antenv"
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "ERROR: Virtualenv not found in $VENV_DIR!"
    exit 1
fi

source "$VENV_DIR/bin/activate"

export PYTHONPATH="$PROJECT_DIR"
export DJANGO_SETTINGS_MODULE=devradar.settings

cd "$PROJECT_DIR"

python -m celery -A devradar worker --loglevel=info
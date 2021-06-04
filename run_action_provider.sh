#!/bin/sh

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cd $SCRIPTPATH

python3 -m pip install --user --upgrade poetry

~/.local/bin/poetry install

.venv/bin/gunicorn --config deploy/gunicorn_config.py esgf_automate.action_provider_main

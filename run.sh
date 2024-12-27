#!/bin/sh

cd `dirname $0`

uv venv --python 3.12.8
source .venv/bin/activate
python3 -m pip install -r requirements.txt -U 

# Be sure to use `exec` so that termination signals reach the python process
exec python3 src/main.py $@
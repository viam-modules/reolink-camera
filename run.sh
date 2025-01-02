#!/bin/bash

cd `dirname $0`

source .venv/bin/activate

# Be sure to use `exec` so that termination signals reach the python process
exec python3 src/main.py $@
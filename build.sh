#!/bin/bash
cd `dirname $0`

echo `pwd`

source "$HOME/.local/bin/env"
source .venv/bin/activate

if ! pip install pyinstaller -Uq; then
    exit 1
fi

python3 -m PyInstaller --onefile --hidden-import="googleapiclient" src/main.py
tar -czvf dist/archive.tar.gz ./dist/main

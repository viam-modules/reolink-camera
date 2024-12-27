#!/bin/bash
cd `dirname $0`

# Desired version of Python to build with
PYTHON_VERSION="3.12"

#for uv
if [ -f "$HOME/.local/bin/env" ]; then
    source "$HOME/.local/bin/env"
fi

# Check if pyenv is installed and install Python version if needed
if command -v uv >/dev/null; then
    echo "uv found. Creating virtual environment and installing packages..."
    if ! uv venv --python $PYTHON_VERSION; then
        echo "Failed to create virtual environment"
        exit 1
    fi

    if ! uv pip install -r requirements.txt; then
        echo "Failed to install packages"
        exit 1
    fi
fi

source .venv/bin/activate

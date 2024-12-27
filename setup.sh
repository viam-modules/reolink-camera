#!/bin/sh
cd `dirname $0`

# Create a virtual environment to run our code
VENV_NAME="venv"
PYTHON="$VENV_NAME/bin/python"
PYENV="$PYENV_ROOT/bin/pyenv"
PYTHON_VERSION="3.12"

# Check if pyenv is installed and install Python version if needed
if command -v $PYENV >/dev/null; then
    echo "pyenv found, checking Python version..."
    if ! $PYENV versions | grep -q $PYTHON_VERSION; then
        echo "Installing Python $PYTHON_VERSION using pyenv..."
        if ! $PYENV install $PYTHON_VERSION -s; then
            echo "Failed to install Python $PYTHON_VERSION" >&2
            exit 1
        fi
    fi

    # Set local Python version and create virtualenv
    if ! $PYENV local $PYTHON_VERSION; then
        echo "Failed to set local Python version" >&2
        exit 1
    fi
fi

# Check if Python version meets minimum requirement
if ! python3 -c "import sys; exit(0 if sys.version_info >= tuple(map(int, '$PYTHON_VERSION'.split('.'))) else 1)" 2>/dev/null; then
    echo "Python version $PYTHON_VERSION or higher is required" >&2
    exit 1
fi

# Create a virtual environment
if ! python3 -m venv $VENV_NAME >/dev/null 2>&1; then
    echo "Failed to create virtualenv."
        exit 1
    fi
fi

# remove -U if viam-sdk should not be upgraded whenever possible
# -qq suppresses extraneous output from pip
echo "Virtualenv found/created. Installing/upgrading Python packages..."
if ! [ -f .installed ]; then
    if ! $PYTHON -m pip install -r requirements.txt -Uqq; then
        exit 1
    else
        touch .installed
    fi
fi

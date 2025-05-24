#!/usr/bin/env bash

set -e
set -u

# Remove existing virtual environment
rm -rf .venv

# Create a new virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

pip install -r requirements.txt

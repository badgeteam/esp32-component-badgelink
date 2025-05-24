#!/usr/bin/env bash

set -e
set -u

# Install the virtual environment if it does not exist
if [[ ! -d ".venv" ]]; then
./install.sh
fi

# Activate the virtual environment
source .venv/bin/activate

# Run BadgeLink
python badgelink.py "$@"

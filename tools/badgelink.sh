#!/usr/bin/env bash

set -e
set -u

script_dir=$(dirname $(realpath $0))
echo $script_dir

# Install the virtual environment if it does not exist
if [[ ! -d "$script_dir/.venv" ]]; then
    pushd $script_dir
    ./install.sh
    popd
fi

# Activate the virtual environment
source $script_dir/.venv/bin/activate

# Run BadgeLink
python $script_dir/badgelink.py "$@"

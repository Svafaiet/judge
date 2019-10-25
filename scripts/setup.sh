#!/usr/bin/bash

set -eu

BASEDIR=$(dirname "$0")
cd "$BASEDIR/.."

pip install -r requirements.txt


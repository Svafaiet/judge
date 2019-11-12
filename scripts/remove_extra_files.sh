#!/usr/bin/env bash

find $1 -path "*/migrations/*.py" -not -name "__init__.py" -delete
find $1 -path "*/migrations/*.pyc"  -delete

find $1 -path "db.sqlite3" -delete

#!/bin/bash -
#
# start server

export DEBUG=true

cd $(dirname $0)
test -d venv && source venv/bin/activate

exec python web.py

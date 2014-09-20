#!/bin/bash -
#
# start server

cd $(dirname $0)
source venv/bin/activate
exec python web.py

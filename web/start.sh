#!/bin/bash -
#
# start server

cd $(dirname $0)

if test -d venv
then
	source venv/bin/activate
fi

exec python web.py

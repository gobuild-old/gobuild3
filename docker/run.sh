#!/bin/bash -
#
export UMASK=002
export PATH=$PATH:$GOPATH/bin

test "X$1" == "Xbash" && exec bash

/usr/bin/timeout ${TIMEOUT-30m} "$@"
RET=$?
if test $RET -ne 0
then
	echo "Exit code $RET"
fi
exit $?

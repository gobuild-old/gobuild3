#!/bin/bash -
#
export UMASK=002
export PATH=$PATH:$GOPATH/bin

if test "X$1" == "Xbash"
then
	exec bash
fi

if test -n "$HTTP_PROXY"
then
	git config --global http.proxy "$HTTP_PROXY"
fi

/usr/bin/timeout ${TIMEOUT-30m} python /build/crosscompile.py "$@"
RET=$?
if test $RET -ne 0
then
	echo "Exit code $RET"
fi
exit $RET

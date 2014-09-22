#!/bin/bash -
#
/usr/bin/timeout ${TIMEOUT-30m} "$@"
RET=$?
if test $RET -ne 0
then
	echo "Exit code $RET"
fi
exit $?

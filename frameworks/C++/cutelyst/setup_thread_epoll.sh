#!/bin/bash

DRIVER=
UWSGI=
NGINX=
PROCESS_OR_THREAD=-t
export CUTELYST_EVENT_LOOP_EPOLL=1

source ${TROOT}/config.sh

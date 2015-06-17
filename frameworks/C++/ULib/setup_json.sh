#!/bin/bash

# 1. Change ULib Server (userver_tcp) configuration
sed -i "s|TCP_LINGER_SET .*|TCP_LINGER_SET 0|g"									  $IROOT/ULib/benchmark.cfg
sed -i "s|LISTEN_BACKLOG .*|LISTEN_BACKLOG 256|g"								  $IROOT/ULib/benchmark.cfg
sed -i "s|PREFORK_CHILD .*|PREFORK_CHILD ${MAX_THREADS}|g"					  $IROOT/ULib/benchmark.cfg
sed -i "s|CLIENT_FOR_PARALLELIZATION .*|CLIENT_FOR_PARALLELIZATION 100|g" $IROOT/ULib/benchmark.cfg

# 2. make use of FIFO scheduling policy possible
sudo setcap cap_sys_nice,cap_sys_resource,cap_net_bind_service,cap_net_raw+eip $IROOT/ULib/bin/userver_tcp
sudo getcap -v                                                                 $IROOT/ULib/bin/userver_tcp

RTPRIO=`ulimit -r`

# 3. Start ULib Server (userver_tcp)
export UMEMPOOL="56,0,0,40,150,-24,-13,-20,0"

CMD="$IROOT/ULib/bin/userver_tcp -c $IROOT/ULib/benchmark.cfg"

if [ $RTPRIO -eq 99 ]; then
	$CMD &
else
   sudo /bin/bash -c "ulimit -r 99 && exec /bin/su $USER -p -c \"UMEMPOOL=$UMEMPOOL $CMD\"" &
fi

#!/bin/sh
stack_size=1
cache_size=240
meta_size=192

# Factor in Ruby's per-thread overhead...
avail_mem=$(awk '/^MemAvailable/ { print int(0.7 * $2 / 1024) - ( \
  $ENVIRON["MAX_CONCURRENCY"] * $ENVIRON["THREAD_FACTOR"] \
); exit }' /proc/meminfo)

# ...as well as Java's per-thread stack size.
heap_size=$(( avail_mem - meta_size - cache_size - (
  stack_size * MAX_CONCURRENCY * THREAD_FACTOR
) ))

JRUBY_OPTS="-J-server -J-XX:+AggressiveOpts -J-Djava.net.preferIPv4Stack=true"
JRUBY_OPTS="$JRUBY_OPTS -J-XX:+UseSerialGC"
#JRUBY_OPTS="$JRUBY_OPTS -J-XX:+UseG1GC -J-XX:MaxGCPauseMillis=100"
JRUBY_OPTS="$JRUBY_OPTS -J-Xms${heap_size}m -J-Xmx${heap_size}m"
JRUBY_OPTS="$JRUBY_OPTS -J-Xss${stack_size}m"
JRUBY_OPTS="$JRUBY_OPTS -J-XX:MaxMetaspaceSize=${meta_size}m"
JRUBY_OPTS="$JRUBY_OPTS -J-XX:ReservedCodeCacheSize=${cache_size}m"

export JRUBY_OPTS

#!/bin/bash

fw_dependsmysql java sbt

sed -i 's|127.0.0.1|'${DBHOST}'|g' play2-java-ebean-hikaricp/conf/application.conf

cd play2-java-ebean-hikaricp

rm -rf target/universal/stage/RUNNING_PID

sbt stage
target/universal/stage/bin/play2-java-ebean-hikaricp &

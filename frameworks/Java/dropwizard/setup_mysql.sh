#!/bin/bash

fw_depends mysql java maven

sed -i 's|url: jdbc:mysql://.*/hello_world|url: jdbc:mysql://'"${DBHOST}"':3306/hello_world|g' hello-world-mysql.yml

mvn -P mysql clean package

java -server $JAVA_OPTS -jar target/hello-world-0.0.1-SNAPSHOT.jar server hello-world-mysql.yml &

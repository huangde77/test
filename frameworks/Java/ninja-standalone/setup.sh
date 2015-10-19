#!/bin/bash

sed -i 's|mysql://.*:3306|mysql://'"${DBHOST}"':3306|g' src/main/java/conf/application.conf

fw_depends java7 maven

mvn clean compile assembly:single

java -Dninja.port=8080 -jar target/ninja-standalone-0.0.1-SNAPSHOT-jar-with-dependencies.jar &

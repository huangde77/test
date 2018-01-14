#!/bin/bash

fw_depends java sbt

sbt 'oneJar' -batch

java -server -Xms1g -Xmx1g -XX:NewSize=512m -XX:MaxNewSize=512m -XX:+UseG1GC -XX:MaxGCPauseMillis=10 -XX:-UseBiasedLocking -XX:+AlwaysPreTouch -jar target/scala-2.12/colossus*one-jar.jar

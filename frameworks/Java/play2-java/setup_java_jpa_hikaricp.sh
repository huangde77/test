#!/bin/bash

fw_depends mysql java sbt

cd play2-java-jpa-hikaricp

rm -rf target/ project/target/ project/project/

sbt stage
target/universal/stage/bin/play2-java-jpa-hikaricp &

#!/bin/bash

fw_depends rvm java7 jruby-1.7.13

rvm jruby-1.7.13 do bundle install --gemfile=$TROOT/Gemfile

DB_HOST=${DBHOST} rvm jruby-1.7.13 do bundle exec torqbox -b 0.0.0.0 -E production &

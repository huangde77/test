# frozen_string_literal: true

# Bundler.require :default
require_relative 'hello_world'

# use Rack::ContentLength
run HelloWorld.new
# require "erb"
# require "yaml"

# $: << "."

# DB_CONFIG = YAML.load(ERB.new(File.read("config/database.yml")).result)

# if RUBY_PLATFORM == "java"
#  require "app/jruby_impl"
#  run App::JRuby
# else
#  require "app/ruby_impl"
#  run App::Ruby
# end

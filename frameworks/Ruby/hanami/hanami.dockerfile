FROM techempower/ruby-2.4:0.1

ADD ./ /hanami

WORKDIR /hanami

RUN bundle install --jobs=4 --gemfile=/hanami/Gemfile --path=/hanami/hanami/bundle

CMD DB_HOST=TFB-database bundle exec puma -t 8:32 -w 8 --preload -b tcp://0.0.0.0:8080 -e production

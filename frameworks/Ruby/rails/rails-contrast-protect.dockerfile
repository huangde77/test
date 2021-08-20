FROM ruby:3.0

RUN apt-get update -yqq && apt-get install -yqq --no-install-recommends redis-server

EXPOSE 8080
WORKDIR /rails

COPY ./Gemfile* /rails/

ENV BUNDLE_WITHOUT=mysql
RUN bundle config set force_ruby_platform true
RUN bundle install --jobs=8

COPY . /rails/

ENV RAILS_ENV=production_postgresql
ENV PORT=8080
ENV REDIS_URL=redis://localhost:6379/0/cache

# Start Contrast Additions
COPY contrast-agent.gem contrast-agent.gem
COPY contrast_security.yaml /etc/contrast/contrast_security.yaml

ENV CONTRAST__ASSESS__ENABLE=false
ENV CONTRAST__PROTECT__ENABLE=true

run bundle exec gem install ./contrast-agent.gem --platform ruby

RUN bundle add contrast-agent
# End Contrast Additions

CMD ./run-with-redis.sh
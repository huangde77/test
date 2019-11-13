FROM ubuntu:19.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -yqq && apt-get install -yqq software-properties-common > /dev/null
RUN LC_ALL=C.UTF-8 add-apt-repository ppa:ondrej/php
RUN apt-get update -yqq > /dev/null && \
    apt-get install -yqq php7.3 php7.3-common php7.3-cli php7.3-mysql  > /dev/null

RUN apt-get install -yqq composer > /dev/null

RUN apt-get install -y php-pear php-dev libevent-dev > /dev/null
RUN printf "\n\n /usr/lib/x86_64-linux-gnu/\n\n\nno\n\n\n" | pecl install event > /dev/null && echo "extension=event.so" > /etc/php/7.3/cli/conf.d/event.ini

COPY deploy/fpm/php.ini /etc/php/7.3/fpm/php.ini

ADD ./ /hamlet
WORKDIR /hamlet

RUN composer require hamlet-framework/http-workerman:dev-master --quiet
RUN composer require hamlet-framework/db-pdo:dev-master --quiet
RUN composer update --no-dev --quiet

CMD php /hamlet/workerman.php start

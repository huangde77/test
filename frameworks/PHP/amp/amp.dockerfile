FROM ubuntu:21.10

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -yqq && apt-get install -yqq software-properties-common > /dev/null
RUN LC_ALL=C.UTF-8 add-apt-repository ppa:ondrej/php
RUN apt-get update -yqq > /dev/null && \
    apt-get install -yqq git unzip wget curl build-essential \
    php8.1-cli php8.1-mbstring php8.1-dev php8.1-xml php8.1-curl > /dev/null

# An extension is required!
# We deal with concurrencies over 1k, which stream_select doesn't support.
RUN wget http://pear.php.net/go-pear.phar --quiet && php go-pear.phar
#RUN apt-get install -y libuv1-dev > /dev/null
RUN apt-get install -y libevent-dev > /dev/null
#RUN pecl install uv-0.2.4 > /dev/null && echo "extension=uv.so" > /etc/php/8.1/cli/conf.d/uv.ini
RUN pecl install event-3.0.6 > /dev/null && echo "extension=event.so" > /etc/php/8.1/cli/conf.d/event.ini

ADD ./ /amp
WORKDIR /amp

COPY deploy/conf/* /etc/php/8.1/cli/conf.d/

COPY --from=composer:latest /usr/bin/composer /usr/local/bin/composer

RUN composer install --prefer-dist --optimize-autoloader --no-dev --quiet

EXPOSE 8080

CMD php /amp/vendor/bin/cluster /amp/server.php

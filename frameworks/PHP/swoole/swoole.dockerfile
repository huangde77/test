FROM php:7.4

RUN pecl install swoole > /dev/null && \
    docker-php-ext-enable swoole

WORKDIR /swoole
COPY swoole-server.php swoole-server.php
COPY php.ini /usr/local/etc/php/

CMD php swoole-server.php

FROM phpswoole/swoole:5.1.3-php8.3

RUN docker-php-ext-install pcntl opcache curl > /dev/null

RUN echo "opcache.enable_cli=1" >> /usr/local/etc/php/conf.d/docker-php-ext-opcache.ini
RUN echo "opcache.jit=1205" >> /usr/local/etc/php/conf.d/docker-php-ext-opcache.ini
RUN echo "opcache.jit_buffer_size=128M" >> /usr/local/etc/php/conf.d/docker-php-ext-opcache.ini

WORKDIR /laravel
COPY --link . .

RUN mkdir -p /laravel/bootstrap/cache /laravel/storage/logs /laravel/storage/framework/sessions /laravel/storage/framework/views /laravel/storage/framework/cache

COPY --link deploy/laravel-s/composer.json .

RUN echo "LARAVELS_LISTEN_IP=0.0.0.0" >> .env
RUN echo "LARAVELS_LISTEN_PORT=8080" >> .env

RUN composer install -a --no-dev --quiet
RUN php artisan optimize
RUN php artisan laravels publish

EXPOSE 8080

ENTRYPOINT [ "php", "bin/laravels", "start" ]

FROM ubuntu:16.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt update -yqq
RUN apt install -yqq software-properties-common
RUN LC_ALL=C.UTF-8 add-apt-repository ppa:ondrej/php
RUN apt update -yqq
RUN apt install -yqq nginx git unzip php7.2 php7.2-common php7.2-cli php7.2-fpm php7.2-mysql

COPY deploy/conf/* /etc/php/7.2/fpm/

ADD ./ /fat-free
WORKDIR /fat-free

ENV F3DIR="/fat-free/src"

RUN git clone "https://github.com/bcosca/fatfree-core.git" src
RUN cd src && git checkout -q "069ccd84afd2461c7ebb67f660c142f97577e661" # v3.5.2-dev

RUN chmod -R 777 /fat-free

CMD service php7.2-fpm start && \
    nginx -c /fat-free/deploy/nginx.conf -g "daemon off;"

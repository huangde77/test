FROM ubuntu:16.04

ADD ./ /urweb
WORKDIR /urweb

RUN apt update -yqq && apt install -yqq build-essential wget libssl-dev libpq-dev libmysqlclient-dev urweb

RUN urweb -db "dbname=hello_world user=benchmarkdbuser password=benchmarkdbpass host=tfb-database" bench

CMD ./bench.exe -q -k -t $((2 * $(nproc)))

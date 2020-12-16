FROM buildpack-deps:focal

RUN apt-get update -yqq
RUN apt-get install -yqq clang libboost-context-dev libboost-dev wget
RUN apt-get install -yqq bison flex

COPY ./ ./

RUN ./compile_libpq.sh
ENV LD_LIBRARY_PATH=/usr/lib

CMD ./compile.sh TFB_PGSQL 667f439040821d981923492e59749b87005268e4

FROM haskell:7.10.3

RUN apt update -yqq
RUN apt install -yqq xz-utils make > /dev/null
RUN apt install -yqq libpq-dev libmysqlclient-dev pkg-config libpcre3 libpcre3-dev > /dev/null

COPY ./yesod-mysql-mongo ./

RUN stack build -j$(nproc) --skip-ghc-check --no-terminal

CMD stack exec yesod-mysql-mongo -- $(nproc) tfb-database +RTS -A32m -N$(nproc)

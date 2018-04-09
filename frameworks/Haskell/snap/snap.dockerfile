FROM haskell:8.2.1

RUN apt update -yqq && apt install -yqq xz-utils make libmysqlclient-dev pkg-config

COPY ./bench /snap
WORKDIR /snap

RUN stack upgrade
RUN stack --allow-different-user build --install-ghc

CMD stack --allow-different-user exec snap-bench -- +RTS -A4M -N -qg2 -I0 -G2

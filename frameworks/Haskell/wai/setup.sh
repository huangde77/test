FROM tfb/haskell:latest

COPY ./bench ./

RUN stack --allow-different-user build --install-ghc

CMD stack --allow-different-user exec bench -- ${CPU_COUNT} ${DBHOST} +RTS -A32m -N${CPU_COUNT}

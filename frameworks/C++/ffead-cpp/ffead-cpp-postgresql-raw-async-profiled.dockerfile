FROM sumeetchhetri/ffead-cpp-5.0-sql-raw-async-profiled-base:5.2

ENV IROOT=/installs

WORKDIR /

CMD ./run_ffead.sh ffead-cpp-5.0-sql emb postgresql-raw-async memory

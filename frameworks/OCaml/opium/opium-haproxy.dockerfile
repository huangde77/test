FROM ocurrent/opam:alpine-3.12-ocaml-4.11

USER root

RUN apk add --no-cache make m4 postgresql-dev libev-dev libffi-dev linux-headers

WORKDIR /web

RUN	opam init --disable-sandboxing --auto-setup\
      && opam install dune\
      && opam clean -a -c -s --logs

COPY src/opi.opam src/Makefile /web/

RUN make install-ci

COPY ./src /web

RUN eval $(opam env) ; dune build --profile release ./bin/main.exe

# try to keep everything above here in sync with opium.dockerfile for more efficent use of docker build cache
RUN apk add haproxy
COPY haproxy.cfg /etc/haproxy/haproxy.cfg
COPY start-servers.sh ./start-servers.sh
RUN chmod +x ./start-servers.sh

CMD /web/start-servers.sh ; /usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -q

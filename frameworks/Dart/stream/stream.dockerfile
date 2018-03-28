FROM techempower/nginx:0.1

FROM techempower/dart-lang:0.1

COPY --from=0 /nginx /nginx

ENV NGINX_HOME="/nginx"
ENV PATH=/nginx/sbin:${PATH}

ADD ./ /stream
WORKDIR /stream

RUN pub upgrade

RUN chmod -R 777 /stream

RUN ./nginx-conf.sh

CMD  ./start-servers.sh && sleep 20 && nginx -c /stream/nginx.conf -g "daemon off;"

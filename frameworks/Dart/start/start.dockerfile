FROM techempower/nginx:0.1

FROM techempower/dart-lang:0.1

COPY --from=0 /nginx /nginx

ENV NGINX_HOME="/nginx"
ENV PATH=/nginx/sbin:${PATH}

ADD ./ /start
WORKDIR /start

RUN pub upgrade

RUN chmod -R 777 /start

RUN ./nginx-conf.sh

CMD  ./start-servers.sh && sleep 20 && nginx -c /start/nginx.conf -g "daemon off;"

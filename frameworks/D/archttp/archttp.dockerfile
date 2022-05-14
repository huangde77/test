FROM debian:sid

ADD ./ /archttp
WORKDIR /archttp

RUN apt-get update -yqq && apt-get install -yqq ldc dub

RUN dub build -b release --compiler=ldc2 --verbose

EXPOSE 1111

CMD ["./archttp-server"]

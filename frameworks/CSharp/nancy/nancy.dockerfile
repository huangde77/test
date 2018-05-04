FROM mono:5.10.0.160
RUN apt update -yqq
RUN apt install -yqq nginx wget mono-fastcgi-server > /dev/null

WORKDIR /nancy
COPY lib lib
COPY NancyModules NancyModules
COPY src src
COPY nginx.conf nginx.conf
COPY run.sh run.sh

RUN xbuild src/NancyBenchmark.csproj /t:Clean
RUN xbuild src/NancyBenchmark.csproj /p:Configuration=Release

CMD bash run.sh

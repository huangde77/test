FROM tfb/gradle:latest
ADD ./ /hexagon
WORKDIR /hexagon
RUN gradle -x test
ENV DBSTORE mongodb
ENV WEBENGINE undertow
CMD build/install/hexagon/bin/hexagon

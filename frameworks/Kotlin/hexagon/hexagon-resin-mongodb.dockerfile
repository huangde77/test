#
# BUILD
#
FROM gradle:6.6-jdk11 AS gradle_build
USER root
WORKDIR /hexagon

COPY src src
COPY build.gradle build.gradle
COPY gradle.properties gradle.properties
RUN gradle --quiet --exclude-task test

#
# RUNTIME
#
FROM adoptopenjdk:11-jre-hotspot-bionic
ENV DBSTORE mongodb
ENV MONGODB_DB_HOST tfb-database
ENV RESIN http://caucho.com/download/resin-4.0.65.tar.gz

WORKDIR /resin
RUN curl -sL $RESIN | tar xz --strip-components=1
RUN rm -rf webapps/*
COPY --from=gradle_build /hexagon/build/libs/ROOT.war webapps/ROOT.war
CMD ["java", "-jar", "lib/resin.jar", "console"]

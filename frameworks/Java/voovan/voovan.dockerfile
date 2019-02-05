FROM maven:3.5.3-jdk-11-slim as maven
WORKDIR /voovan
COPY pom.xml pom.xml
COPY src src
COPY config/framework.properties config/framework.properties
RUN mvn package -q

FROM openjdk:11-jdk-slim
WORKDIR /voovan
COPY --from=maven /voovan/target/voovan-bench-0.1-jar-with-dependencies.jar app.jar
CMD ["java", "-server", "-XX:+UseParallelGC", "-XX:+UseNUMA", "--illegal-access=warn", "-Djdk.attach.allowAttachSelf=true", "-cp", "./config:voovan.jar:app.jar", "org.voovan.VoovanTFB"]

FROM tfb/maven:latest as maven
ADD ./ /activeweb
WORKDIR /activeweb
RUN mvn clean package -DskipTests

FROM tfb/resin:latest
COPY --from=maven /activeweb/target/activeweb.war ${RESIN_HOME}/webapps/ROOT.war

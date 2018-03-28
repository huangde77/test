FROM techempower/sbt:0.1

COPY ./play2-scala-reactivemongo ./

RUN sbt stage

CMD target/universal/stage/bin/play2-scala-reactivemongo -Dplay.server.provider=play.core.server.AkkaHttpServerProvider

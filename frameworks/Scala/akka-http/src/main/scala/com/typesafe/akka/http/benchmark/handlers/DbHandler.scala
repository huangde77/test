package com.typesafe.akka.http.benchmark.handlers

import akka.http.scaladsl.model.HttpCharsets._
import akka.http.scaladsl.model.MediaTypes._
import akka.http.scaladsl.model.{ HttpEntity, HttpResponse, StatusCodes }
import akka.http.scaladsl.server.Directives._
import com.typesafe.akka.http.benchmark.Infrastructure
import com.typesafe.akka.http.benchmark.datastore.DataStore
import com.typesafe.akka.http.benchmark.entity.World
import com.typesafe.akka.http.benchmark.util.RandomGenerator
import spray.json.{ DefaultJsonProtocol, RootJsonFormat }

import scala.concurrent.ExecutionContext
import scala.util.{ Failure, Success }

trait DbHandler { _: Infrastructure with DataStore with RandomGenerator =>
  import DbHandler.Protocols._

  def dbEndpoint = get {
    path("db") {
      onComplete(response) {
        case Success(record) => complete(record)
        case Failure(t)      => failWith(t)
      }
    }
  }

  private def response = {
    val id = nextRandomInt
    findOne(id).map {
      record => HttpResponse(StatusCodes.OK, entity = HttpEntity(record.toResponse.toJson.toString()).withContentType(`application/json`))
    }
  }

}

object DbHandler {

  object Protocols extends DefaultJsonProtocol {

    case class Response(id: Int, randomNumber: Int)

    implicit val responseFormat: RootJsonFormat[Response] = jsonFormat2(Response.apply)

    implicit class ToResponse(record: World) {
      def toResponse = Response(record.id, record.randomNumber)
    }

  }

}
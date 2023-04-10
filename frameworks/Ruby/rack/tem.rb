# frozen_string_literal: true

module Tem

  QUERY_RANGE = 1..10_000 # range of IDs in the Fortune DB
  ALL_IDS = QUERY_RANGE.to_a # enumeration of all the IDs in fortune DB
  MIN_QUERIES = 1 # min number of records that can be retrieved
  MAX_QUERIES = 500 # max number of records that can be retrieved
  FORTUNTE_FOOTER='<!DOCTYPE html>
      <html>
      <head>
        <title>Fortune</title>
      </head>
      <body>
        <table>
          <tr>
            <th>id</th>
            <th>message</th>
          </tr>'


  def self.call(_req)
    f_1 = $pool.with do |conn|
            conn.exec(<<-SQL)

              SELECT id, message FROM fortune

            SQL
          end

    f_2 = f_1.map(&:to_h).
            append({ 'id' => '0', 'message' => 'Additional fortune added at request time.' }).
              sort { |x,y| x['message'] <=> y['message'] }.
                map { |f| "<tr><td>#{ f['id'] }</td><td>#{ Rack::Utils.escape_html(f['message']) }</td></tr>" }.
                  join

    html_response(<<-HTML)
      <!DOCTYPE html>
      <html>
        <head>
          <title>Fortune</title>
        </head>
        <body>
          <table>
            <tr>
              <th>id</th>
              <th>message</th>
            </tr>
            #{ f_2 }
          </table>
        </body
      </html>
    HTML
  end


  def self.html_response(str = '')
    [
        200,
        {
            'Content-Type' => 'text/html; charset=utf-8',
            'Date'         => Time.now.utc.httpdate,
            'Server'       => 'Rack'
        },
        [str]
    ]
  end

  def self.json_response(obj = {})
    [
        200,
        {
            'Content-Type' => 'application/json',
            'Date'         => Time.now.utc.httpdate,
            'Server'       => 'Rack'
        },
        [Oj.dump(obj, { :mode => :strict })]
    ]
  end

  def self.plain_response(str = '')
    [
        200,
        {
            'Content-Type' => 'text/plain',
            'Date'         => Time.now.utc.httpdate,
            'Server'       => 'Rack'
        },
        [str]
    ]
  end
end

module Tem
  class Postgres
    def initialize(pool_size=512)
      database_url = ENV['DATABASE_URL'] || 'postgres://benchmarkdbuser:benchmarkdbpass@tfb-database:5438/hello_world'

      @pool =ConnectionPool.new(size: 256, timeout: 5) do
        PG::Connection.new(database_url)
      end
  end
end




get "json", to: JsonController.action(:index)
get "db", to: "hello_world#db"
get "queries", to: "hello_world#query"
get "fortunes", to: "hello_world#fortune"
get "updates", to: "hello_world#update"
get "plaintext", to: PlaintextController.action(:index)
get "cached", to: "hello_world#cached_query"


ENV['RACK_ENV']=='development'  && ENV['PG'] || "test"


connectionString =
  "postgres://benchmarkdbuser:benchmarkdbpass@%s/hello_world?sslmode=disable"
worldSelect = "SELECT id, randomNumber FROM World WHERE id = $1"
worldUpdate = "UPDATE World SET randomNumber = $1 WHERE id = $2"
fortuneSelect = "SELECT id, message FROM Fortune"
worldRowCount = 10_000
maxConnections = 256

dbHost = "tfb-database"
dbPort = 5432
dbUser = "benchmarkdbuser"
dbPaswd = "benchmarkdbpass"
dbName = "hello_world"

worldSelectSQL = "SELECT id, randomNumber FROM World WHERE id = $1"
worldSelectCacheSQL = "SELECT id, randomNumber FROM World LIMIT $1"
worldUpdateSQL = "UPDATE World SET randomNumber = $1 WHERE id = $2"
fortuneSelectSQL = "SELECT id, message FROM Fortune"

response.set_header("Server", "rails")
response.set_header("Date", Time.now.httpdate)

# frozen_string_literal: true

class HelloWorldController < ApplicationController
  QUERY_RANGE = 1..10_000 # range of IDs in the Fortune DB
  ALL_IDS = QUERY_RANGE.to_a # enumeration of all the IDs in fortune DB
  MIN_QUERIES = 1 # min number of records that can be retrieved
  MAX_QUERIES = 500 # max number of records that can be retrieved

  def plaintext
    render plain: "Hello, World!"
  end

  def json
    render json: JSON.generate({ message: "Hello, World!" })
  end

  def db
    render json: World.find(random_id)
  end

  def query
    results = ALL_IDS.sample(query_count).map { |id| World.find(id) }

    render json: results
  end

  def cached_query
    items =
      Rails
        .cache
        .fetch_multi(*ALL_IDS.sample(query_count)) do |id|
          World.find(id).as_json
        end

    render json: items.values
  end

  def fortune
    @fortunes = Fortune.all.to_a
    @fortunes << Fortune.new(
      id: 0,
      message: "Additional fortune added at request time."
    )
    @fortunes.sort_by!(&:message)
  end

  def update
    worlds =
      Array.new(query_count) do
        world = World.find(random_id)
        new_value = random_id
        new_value = random_id until new_value != world.randomNumber
        world.update_columns(randomNumber: new_value)
        world
      end

    render json: worlds
  end

  private

  def query_count
    queries = params[:queries].to_i
    return MIN_QUERIES if queries < MIN_QUERIES
    return MAX_QUERIES if queries > MAX_QUERIES

    queries
  end

  def random_id
    Random.rand(QUERY_RANGE)
  end
end

# frozen_string_literal: true

# Our Rack application to be executed by rackup
class HelloWorld
  DEFAULT_HEADERS = {}.tap do |h|
    h['Server'] = SERVER_STRING if SERVER_STRING
  end.freeze

  def bounded_queries(env)
    params = Rack::Utils.parse_query(env['QUERY_STRING'])

    queries = params['queries'].to_i
    return QUERIES_MIN if queries < QUERIES_MIN
    return QUERIES_MAX if queries > QUERIES_MAX
    queries
  end

  # Return a random number between 1 and MAX_PK
  def rand1
    Sysrandom.random_number(MAX_PK).succ
  end

  def db
    World.with_pk(rand1).values
  end

  def queries(env)
    Array.new(bounded_queries(env)) do
      World.with_pk(rand1).values
    end
  end

  def fortunes
    fortunes = Fortune.all
    fortunes << Fortune.new(
      :id=>0,
      :message=>'Additional fortune added at request time.'
    )
    fortunes.sort_by!(&:message)

    html = <<~'HTML'
      <!DOCTYPE html>
      <html>
      <head>
        <title>Fortunes</title>
      </head>

      <body>

      <table>
      <tr>
        <th>id</th>
        <th>message</th>
      </tr>
    HTML

    fortunes.each do |fortune|
      html += <<~"HTML"
      <tr>
        <td>#{Rack::Utils.escape_html(fortune.id)}</td>
        <td>#{Rack::Utils.escape_html(fortune.message)}</td>
      </tr>
      HTML
    end

    html += <<~'HTML'
      </table>

      </body>
      </html>
    HTML
  end

  WORLD_BY_ID = World.naked.where(:id=>:$id).prepare(:first, :world_by_id)
  WORLD_UPDATE = World.where(:id=>:$id).prepare(:update, :world_update, :randomnumber=>:$randomnumber)

  def updates(env)
    Array.new(bounded_queries(env)) do
      world = WORLD_BY_ID.(:id=>rand1)
      WORLD_UPDATE.(:id=>world[:id], :randomnumber=>(world[:randomnumber] = rand1))
      world
    end
  end

  def call(env)
    content_type, *body =
      case env['PATH_INFO']
      when '/json'
        # Test type 1: JSON serialization
        ['application/json', JSON.fast_generate(:message=>'Hello, World!')]
      when '/db'
        # Test type 2: Single database query
        ['application/json', JSON.fast_generate(db)]
      when '/queries'
        # Test type 3: Multiple database queries
        ['application/json', JSON.fast_generate(queries(env))]
      when '/fortunes'
        # Test type 4: Fortunes
        ['text/html; charset=utf-8', fortunes]
      when '/updates'
        # Test type 5: Database updates
        ['application/json', JSON.fast_generate(updates(env))]
      when '/plaintext'
        # Test type 6: Plaintext
        ['text/plain', 'Hello, World!']
      end

    return 200,
      DEFAULT_HEADERS.merge(
        'Content-Type'=>content_type,
        'Date'=>Time.now.httpdate
      ),
      body
  end
end
